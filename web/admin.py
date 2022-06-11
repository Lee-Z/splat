from django.contrib import admin
from web import models
from django.contrib import messages
from django.http import JsonResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import requests
from IPy import IP
import geoip2.database
from django.http import HttpResponse
from django.utils.html import format_html
import os
import datetime



#客户端列表显示
class Agent(admin.ModelAdmin):
    list_display = ['ip','statusColored','create_time','purpose','operate']
    search_fields = ['ip', 'state','create_time']
#    list_editable = ['idc_ip','idc_status']
    fields = ['ip','purpose']
    list_filter = ['create_time']

    def statusColored(self, obj):
        if obj.status == 1:
            return format_html('<span style="color:green">{}</span>', '在线')
        elif obj.status ==2:
            return format_html('<span style="color:green">{}</span>', '未注册')
        else:
            return format_html('<span style="color:red">{}</span>', '离线')
    statusColored.short_description = "状态"
    #将上面的列可排序（显示和其他列头一样）
    statusColored.admin_order_field = 'status'

    #页面上面添加按钮
    actions = ['custom_button','pro_scan','port_scan']
    def custom_button(self, request, queryset):
        print(queryset)
        if request.method == 'POST':
            filed_id = request.POST.get('_selected_action')
            print(filed_id)
            models.Active_ip.objects.filter(id=filed_id, status=2).update(status=1)
            status_id = models.Active_ip.objects.filter(id=filed_id).values_list('status')
            print(status_id[0][0])
            if status_id[0][0] == 2:
                models.Active_ip.objects.filter(id=filed_id, status=2).update(status=1)
                messages.add_message(request, messages.SUCCESS, "注册成功")
            elif status_id[0][0] == 1:
                messages.add_message(request, messages.SUCCESS, "已在线状态")
            else:
                messages.add_message(request, messages.SUCCESS, "离线状态")
    # 显示的文本，与django admin一致
    custom_button.short_description = '注册'
    # icon，参考element-ui icon与https://fontawesome.com
    # custom_button.icon = 'fas fa-audio-description'
    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    custom_button.type = 'danger'
    # 给按钮追加自定义的颜色
    custom_button.style = 'color:black;'
    custom_button.confirm = '是否确定注册'

    #进程扫描按钮
    def pro_scan(self, request, queryset):
        skipnext = False
        if request.method == 'POST':
            res_list = list()
            #遍历取出全选,遍历所有勾选的ip地址
            for e in queryset.all():
                try:
                    pro_ip = (models.Active_ip.objects.filter(id=e.id).values_list('ip'))
                    print (pro_ip[0][0])
                    url = "http://%s:8280/maintain/getProcess" % (pro_ip[0][0])
                    new_json = {
                    }
                    res = requests.post(url, json=new_json)
                    if res:
                        # print(type(res.json()))
                        # print(res_list)
                        for x in res.json():
                            #插入数据库
                            # models.IdcScan.objects.create(idc_ip=pro_ip[0][0],idc_command="ps",idc_status='0',idc_value=i)
                            a = models.process_whitelist.objects.filter(whitelist_process=x)
                            if a:
                                print("添加白名单")
                                res_list.append(models.IdcScan(idc_ip=pro_ip[0][0],idc_command="ps",idc_status='1',idc_value=x))
                            else:
                                res_list.append(models.IdcScan(idc_ip=pro_ip[0][0], idc_command="ps", idc_status='0', idc_value=x))
                except:
                    print("未在线")
            models.IdcScan.objects.bulk_create(res_list)
            messages.add_message(request, messages.SUCCESS, '扫描完成')
        # return queryset
    pro_scan.short_description = '进程扫描'
    pro_scan.type = 'danger'
    # 给按钮追加自定义的颜色
    pro_scan.style = 'color:black;'
    pro_scan.confirm = '是否确定扫描'

    #出网检测按钮
    def port_scan(self, request, queryset):
        outgong_dic=list()
        if request.method == 'POST':
            for e in queryset.all():
                try:
                    pro_ip = (models.Active_ip.objects.filter(id=e.id).values_list('ip'))
                    print (pro_ip[0][0])
                    url = "http://%s:8280/maintain/getIp" % (pro_ip[0][0])
                    new_json = {
                    }
                    res = requests.post(url, json=new_json)

                    #该函数为 字典1个key值对应多个value值改成1个key值对应一个value值
                    def itertransfer(mapper):
                        for k, values in mapper.items():
                            for v in values:
                                yield (k, v)
                    for k, v in itertransfer(res.json()):
                        print(k,v.split(':')[0])
                        # ip = IP(v.split(':')[0])
                        ip = IP(v.split(':')[0])
                        nowdate = datetime.datetime.now().date()
                        objs = models.outgonging_detection.objects.filter(outgong_connect=ip,outgong_scan_time__gte=nowdate).values('outgong_id')
                        if objs:
                            #端口扫描今天已存在数据库有该ip访问
                            print('为真有值')
                        else:
                            #外网返回：PUBLIC  内网：PRIVATE  127：LOOPBACK
                            if ip.iptype() == 'PRIVATE' or ip.iptype() == 'LOOPBACK':
                                # print("私网地址")
                                outgong_dic.append(
                                    models.outgonging_detection(outgong_ip=pro_ip[0][0], outgong_connect=v.split(':')[0],outgong_port=v.split(':')[1],outgong_addr="本地地址", outgong_scan_time=k,outgong_network=0))
                            elif ip.iptype() == 'PUBLIC':
                                #根据ip获取地址位置，并插入数据库
                                with geoip2.database.Reader('web/GeoLite2-City.mmdb') as reader:
                                    print(str(ip))
                                    response = reader.city(str(ip))
                                    if response.country.names['zh-CN'] == '中国':
                                        #省会
                                        province = response.subdivisions.most_specific.names['zh-CN']
                                        #城市
                                        city = response.city.names['zh-CN']
                                        # geographical_position = '{}{}'.format(province,city)
                                        geographical_position = '{}'.format(province)
                                        outgong_dic.append(
                                            models.outgonging_detection(outgong_ip=pro_ip[0][0],
                                                                        outgong_connect=v.split(':')[0],
                                                                        outgong_port=v.split(':')[1], outgong_addr=geographical_position,
                                                                        outgong_scan_time=k, outgong_network=1, outgong_regionnum=1))
                                    else:
                                        province = response.subdivisions.most_specific.name
                                        city = response.city.name
                                        geographical_position = '{}'.format(response.country.names['zh-CN'])
                                        outgong_dic.append(
                                            models.outgonging_detection(outgong_ip=pro_ip[0][0],
                                                                        outgong_connect=v.split(':')[0],
                                                                        outgong_port=v.split(':')[1],
                                                                        outgong_addr=geographical_position,
                                                                        outgong_scan_time=k, outgong_network=1,outgong_regionnum=2))
                            else:
                                print("未能识别该地址")
                except:
                    print("报错")

            models.outgonging_detection.objects.bulk_create(outgong_dic)
            messages.add_message(request, messages.SUCCESS, '扫描完成')
    port_scan.short_description = '端口扫描'
    #primary 主要按钮.success 成功按钮.info 信息  warning 警告  danger 危险
    port_scan.type = 'success'
    # 给按钮追加自定义的颜色
    port_scan.style = 'color:black;'
    port_scan.confirm = '是否确定扫描'


    #报错
    # @admin.display(description='操作', ordering='id')
    def operate(self, obj):
        #注释的btn1 为弹出提示
        # info_msg = f'这条狗的名字是：{obj.id} 年龄是：{obj.status}'
        # simpleui 用的elementui ,可以使用el的类修改默认样式
        # btn1 = f"""<button onclick="self.parent.app.$msgbox('{info_msg}')"
        #                     class="el-button el-button--warning el-button--small">编辑</button>"""
        change = '{"name": "%s", "icon": "fas fa-user-tie", "url": "/admin/web/active_ip/%d/change/"}' % (obj.id, obj.id)
        btn1 = f"""<button onclick='self.parent.app.openTab({change})'
                             class='el-button el-button--warning el-button--small'>编辑</button>"""
        # 在新标签中打开修改界面，url可以随意指定。自己可以多做尝试
        data = '{"name": "%s", "icon": "fas fa-user-tie", "url": "/admin/web/active_ip/%d/delete/"}' % (obj.id, obj.id)
        btn2 = f"""<button onclick='self.parent.app.openTab({data})'
                             class='el-button el-button--danger el-button--small'>删除</button>"""
        return mark_safe(f"<div>{btn1} {btn2}</div>")
    #以下语法替换 @admin.display(description='操作', ordering='id')
    operate.short_description = '操作'
    operate.admin_order_field = 'id'

#进程白名单显示设置
class process_list(admin.ModelAdmin):
    list_display = ['whitelist_id','whitelist_process','whitelist_time','whitelist_purpose']
    search_fields = ['whitelist_process', 'whitelist_time']
    # list_editable = ['whitelist_process']
    list_filter = ['whitelist_time']
#   #设置哪些字段可以点击进入编辑界面
#     list_display_links = ['id', 'caption']
    # 隐藏增加按钮
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

#ip异常ip名单显示设置
class ipaddress_blacklist(admin.ModelAdmin):
    list_display = ['blacklist_id','blacklist_ip','blacklist_time','blacklist_purpose']
    search_fields = ['blacklist_ip', 'blacklist_time']
    # list_editable = ['whitelist_process']
    list_filter = ['blacklist_time']



# Register your models here.  #short_detail 将id_value做了显示限制
#进程扫描列表显示设置
class Idc(admin.ModelAdmin):
    list_display = ['idc_id', 'idc_ip','idc_command','idc_status', 'idc_time','short_detail','add_whitelist']
    search_fields = ['idc_status', 'idc_ip','idc_value']
#    list_editable = ['idc_ip','idc_status']
    list_filter = ['idc_status']
    #禁用编辑链接
    list_display_links = None
    # 隐藏增加按钮
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False
    # #删除自带添加按钮
    # def has_add_permission(self, request):
    #     return False
    # #删除自带删除按钮
    # def has_delete_permission(self, request, obj=None):
    #     return False
    # @admin.display(description='操作', ordering='id')

    def add_whitelist(self,obj):
    #     #注释的btn1 为弹出提示
    #     # info_msg = f'这条狗的名字是：{obj.idc_id} 年龄是：{obj.idc_id}'
    #     info_msg = models.IdcScan.objects.filter(idc_id=obj.idc_id)
    #     # print(info_msg)
    #     # simpleui 用的elementui ,可以使用el的类修改默认样式
    #     btn1 = f"""<button onclick="highlight_link" name="test1"
    #                         class="el-button el-button--warning el-button--small">添加至白名单</button>"""
    #
    #     # change = '{"name": "%s", "icon": "fas fa-user-tie", "url": "/admin/web/active_ip/%d/change/"}' % (obj.idc_id, obj.idc_id)
        btn1 = f"""<button  id='icon_{obj.idc_id}' onclick='show_pic("{obj.idc_id}")'
                             class='el-button el-button--warning el-button--small'>添加至白名单</button>"""
    #     # 在新标签中打开修改界面，url可以随意指定。自己可以多做尝试
    #     data = '{"icon": "fas fa-user-tie", "url": "web/idcscan"}'
    #     # btn2 = f"""<button onclick='self.parent.app.openTab({data})' name="test2"
    #     btn2 = f"""<button onclick='{data}' name="test2"
    #                          class='el-button el-button--danger el-button--small'>删除</button>"""
    #     btn3 = f"""<form action="/index/" method="post">
    #         <p><input type="submit" value="提交"/></p>
    #     </form>"""
        return mark_safe(f"<div>{btn1}</div>")
    # def img(self, obj):
    #     # 在custom.js里面实现了show_pic函数，onclick进行调用
    #     div = f"""<button id='icon_{obj.idc_id}' src='{obj.idc_ip}'
    #     width='32px' onclick='show_pic()"' />"""
    #     return mark_safe(div)
    add_whitelist.short_description = '操作'
    add_whitelist.admin_order_field = 'idc_id'
    class Media:
        js = ('/static/admin/js/custom.js',
              #   也可以挂载cdn文件，这里仅示例
              #  'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.js',
             )
    #取出自定义列中request 请求操作
    def get_queryset(self, request):
        qs = super(Idc, self).get_queryset(request)
        self.request = request
        if "test1" in request.POST:
            print("点击了加入白名单按钮")
            jincheng = models.IdcScan.objects.all()
            print (jincheng)

        return qs

    def highlight_link(self, request):
        if "test1" in request.POST:
            print("点击了加入白名单按钮2")


# 增加自定义按钮
#     actions = ['make_copy', 'custom_button','delete_button']
#
#     def custom_button(self, request, queryset):
#         messages.add_message(request, messages.SUCCESS, '操作成功123123123123')
#
#     # 显示的文本，与django admin一致
#     custom_button.short_description = '测试按钮'
#     # icon，参考element-ui icon与https://fontawesome.com
#     custom_button.icon = 'fas fa-audio-description'
#
#     # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
#     custom_button.type = 'danger'
#
#     # 给按钮追加自定义的颜色
#     custom_button.style = 'color:black;'
#     custom_button.confirm = '你是否执意要点击这个按钮'
#
#     def make_copy(self, request, queryset):
#         pass
#     make_copy.short_description = '复制员工'
#
#     def delete_button(self,request,queryset):
#         pass
#     delete_button.type = 'danger'
#     delete_button.short_description = '删除员工'
#     delete_button.action_type = 0
#     delete_button.action_url = 'http://www.baidu.com'


#页面上面弹出按钮输入框
#    actions = ('layer_input',)

    def layer_input(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据

        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    layer_input.short_description = '弹出对话框输入'
    layer_input.type = 'success'
    layer_input.icon = 'el-icon-s-promotion'
    # 指定一个输入参数，应该是一个数组

    # 指定为弹出层，这个参数最关键
    layer_input.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '弹出层输入框',
        # 提示信息
        'tips': '这个弹出对话框是需要在admin中进行定义，数据新增编辑等功能，需要自己来实现。',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'name',
            # 显示的文本
            'label': '名称',
            # 为空校验，默认为False
            'require': True
        }, {
            'type': 'select',
            'key': 'type',
            'label': '类型',
            'width': '200px',
            # size对应elementui的size，取值为：medium / small / mini
            'size': 'small',
            # value字段可以指定默认值
            'value': '0',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }]
        }, {
            'type': 'number',
            'key': 'money',
            'label': '金额',
            # 设置默认值
            'value': 1000
        }, {
            'type': 'date',
            'key': 'date',
            'label': '日期',
        }, {
            'type': 'datetime',
            'key': 'datetime',
            'label': '时间',
        }, {
            'type': 'rate',
            'key': 'star',
            'label': '评价等级'
        }, {
            'type': 'color',
            'key': 'color',
            'label': '颜色'
        }, {
            'type': 'slider',
            'key': 'slider',
            'label': '滑块'
        }, {
            'type': 'switch',
            'key': 'switch',
            'label': 'switch开关'
        }, {
            'type': 'input_number',
            'key': 'input_number',
            'label': 'input number'
        }, {
            'type': 'checkbox',
            'key': 'checkbox',
            # 必须指定默认值
            'value': [],
            'label': '复选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }, {
            'type': 'radio',
            'key': 'radio',
            'label': '单选框',
            'options': [{
                'key': '0',
                'label': '收入'
            }, {
                'key': '1',
                'label': '支出'
            }, {
                'key': '2',
                'label': '收益'
            }]
        }]
    }

#网络连接检测显示
class outgonging_detection(admin.ModelAdmin):
    list_display = ['outgong_ip','outgong_connect','outgong_port','outgong_addr','outgong_status','outgong_scan_time','outgong_purpose','outgong_whitelist']
    search_fields = ['outgong_ip','outgong_connect']
    list_filter = ['outgong_status','outgong_network','outgong_scan_time']
    def outgong_whitelist(self,obj):
        btn1 = f"""<button  id='icon_{obj.outgong_id}' onclick='outgongw("{obj.outgong_id}")'
                             class='el-button el-button--warning el-button--small'>添加至黑名单</button>"""
        btn2 = f"""<button  id='icon_{obj.outgong_id}' onclick='outgongw("{obj.outgong_id}")'
                             class='el-button el-button--warning el-button--small'>添加至白名单</button>"""
        return mark_safe(f"<div>{btn1}</div>")
    outgong_whitelist.short_description = '操作'
    outgong_whitelist.admin_order_field = 'outgong_id'
    class Media:
        js = ('/static/admin/js/custom.js',
              #   也可以挂载cdn文件，这里仅示例
              #  'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.js',
             )
    # 禁用编辑链接
    list_display_links = None
    # 隐藏增加按钮
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False

#文件完整性列表显示
class ProjectInfo(admin.ModelAdmin):
    list_display = ['project_name','project_ip','project_scanpath','project_special','project_sete','project_updatetime','operate_action']
    search_fields = ['project_ip']
    list_filter = ['project_sete']
    def operate_action(self, obj):
        btn1 = f"""<button  id='icon_{obj.project_id}' onclick='btn1("{obj.project_id}")'
                             class='el-button el-button--warning el-button--small'>获取</button>"""
        btn2 = f"""<button  id='icon_{obj.project_id}' onclick='btn2("{obj.project_id}")'
                             class='el-button el-button--warning el-button--small'>比对</button>"""
        return mark_safe(f"<div>{btn1}{btn2}</div>")
    #以下语法替换 @admin.display(description='操作', ordering='id')
    operate_action.short_description = '操作'
    operate_action.admin_order_field = 'project_id'
    class Media:
        js = ('/static/admin/js/custom.js',
              #   也可以挂载cdn文件，这里仅示例
              #  'https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.js',
             )


#异常文件信息
class ChangeFile(admin.ModelAdmin):
    list_display = ['change_name','change_ip','change_url','change_state','change_updatetime','change_scantime','change_down']
    search_fields = ['change_name']
    list_filter = ['change_state']
    def change_down(self, obj):
        path = obj.change_id
        # headers = {'Content-Type': 'application/json',
        #            'fileName': obj.change_url
        #            }
        # url = "http://%s:8280/maintain/download" % (obj.change_ip)
        # res = requests.post(url, headers=headers)
        # print(res.text)
        # change_id = os.path.basename(obj.change_id)
        download = "http://127.0.0.1:8092/download?change_id=%s" % (obj.change_id)
        # download = "http://127.0.0.1:8092/download"
        # print('点击了%s' %obj.change_id)
        button_html = "<a  href='{}'>下载文件</a>".format(download)
        # button_html = "<a  href='#'>下载文件</a>"
        return format_html(button_html)
    #以下语法替换 @admin.display(description='操作', ordering='id')
    change_down.short_description = '操作'
    change_down.admin_order_field = 'change_id'
    # 禁用编辑链接
    list_display_links = None
    # 隐藏增加按钮
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        # 禁用删除按钮
        return False



#定时任务信息
class Cron(admin.ModelAdmin):
    list_display = ['cron_name','cron_ip', 'cron_task', 'cron_strategy', 'cron_stat', 'cron_purpose',]
    list_editable = ['cron_stat']
    search_fields = ['cron_ip']
    list_filter = ['cron_ip']
    actions = ['crontbutton','delete_selected']
    def crontbutton(self,request, queryset):
        pass
    crontbutton.short_description = '添加任务'
    # crontbutton.icon = 'fas fa-audio-description'
    crontbutton.type = 'danger'
    crontbutton.style = 'color:black;'
    crontbutton.action_type = 0
    crontbutton.action_url = 'http://127.0.0.1:8092/cronpage'
    #重写删除按钮
    def delete_selected(modeladmin, request, queryset):
        c = 0
        for i in queryset:
            print(i.cron_id)
            cronname = models.cron_info.objects.filter(cron_id=i.cron_id).values('cron_task','cron_name')
            activeid = models.Active_ip.objects.filter(ip=i.cron_ip).values('id')
            if models.scheduler.state == 0:
                models.scheduler.start()
            job_id=cronname[0]['cron_name']+cronname[0]['cron_task']+str(activeid[0]['id'])
            print(job_id)
            models.scheduler.remove_job(job_id=job_id)
            i.delete()
            c += 1
        msg = '成功删除了{}个表管理'.format(c)
        #原作者写的删除后没提示，这里添加
        modeladmin.message_user(request, msg)
    delete_selected.short_description = '删除已选项'


    #隐藏增加按钮
    def has_add_permission(self, request):
        # print("222")
        # jobid = models.cron_info.objects.filter(cron_stat='0').values('cron_name','cron_task','cron_id')
        # for i in jobid:
        #     name = i['cron_name']
        #     task = i['cron_task']
        #     cronid = i['cron_id']
        #     job_id = name+task+str(cronid)
        #     models.scheduler.pause_job(job_id)

        return False
    #重写页面 list_editable  编辑后 保存按钮
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # if obj.cron_stat == 0:
        #     print('++++++++')
        #     print('this is test111')
        #     print('++++++++')
        # elif obj.cron_stat == 1:
        #     print('++++++++')
        #     print('this is test222')
        #     print('++++++++')
        # jobid1 = models.cron_info.objects.filter(cron_stat='0').values('cron_name', 'cron_task', 'cron_id')
        # print(jobid1)
        if models.scheduler.state == 0:
            models.scheduler.start()
        #0 为开启任务  1为暂停任务
        if obj.cron_stat == 0:
            print('恢复定时任务')
            # serverid = models.Active_ip.objects.filter(ip=obj.cron_ip).values('id')
            # print(serverid)
            # for sid in serverid:
            #     serid = sid['id']
            jobid = models.cron_info.objects.filter(cron_stat='0').values('cron_name','cron_task','cron_id')
            for i in jobid:
                name = i['cron_name']
                task = i['cron_task']
                cronid = i['cron_id']
                activeip = models.cron_info.objects.filter(cron_id=cronid).values('cron_ip')
                activeid = models.Active_ip.objects.filter(ip=activeip[0]['cron_ip']).values('id')
                print(activeid)
                job_id = name+task+str(activeid[0]['id'])
                print(job_id)
                # alljob = models.scheduler.get_jobs()
                # print(alljob)
                # 恢复job
                models.scheduler.resume_job(job_id)
        elif obj.cron_stat == 1:
            jobid = models.cron_info.objects.filter(cron_stat='1').values('cron_name', 'cron_task', 'cron_id')
            for i in jobid:
                name = i['cron_name']
                task = i['cron_task']
                cronid = i['cron_id']
                activeip = models.cron_info.objects.filter(cron_id=cronid).values('cron_ip')
                activeid = models.Active_ip.objects.filter(ip=activeip[0]['cron_ip']).values('id')
                job_id = name + task + str(activeid[0]['id'])
                print(job_id)
                # alljob = models.scheduler.get_jobs()
                # print(alljob)
                # 暂停job
                models.scheduler.pause_job(job_id)

        # if obj.action == 1:
        #     # 通过
        #     user_obj = models.UserInfo.objects.get(username=obj.username)
        #     models.UserInfo.objects.filter(username=obj.username).update(money=user_obj.money + obj.money)
        #     print('zidingyi save button')
        # else:
        #     pass

    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)
    #     print("this is save post")
    #     if obj.action == 1:
    #         # 通过
    #         user_obj = models.UserInfo.objects.get(username=obj.username)
    #         models.UserInfo.objects.filter(username=obj.username).update(money=user_obj.money + obj.money)
    #         print("this is save post")
    #     else:
    #         print("this is sava post")



#外网连接
class Expnetwork(admin.ModelAdmin):
    list_display = ['expnetwork_id', 'expnetwork_ip', 'expnetwork_stat', 'expnetwork_purpose','expnetwork_scantime', ]
    # list_editable = ['cron_stat']
    search_fields = ['expnetwork_scantime']
    list_filter = ['expnetwork_scantime']
    actions = ['addnetpage']

    def addnetpage(self, request, queryset):
        pass

    addnetpage.short_description = '添加任务'
    # crontbutton.icon = 'fas fa-audio-description'
    addnetpage.type = 'danger'
    addnetpage.style = 'color:black;'
    addnetpage.action_type = 0
    addnetpage.action_url = 'http://127.0.0.1:8092/addextpage'
    # 禁用编辑链接
    list_display_links = None
    #隐藏增加按钮
    def has_add_permission(self, request):
        return False





#登录页面设置
admin.site.site_header = '运维安全平台'  # 设置header
admin.site.site_title = '运维安全后台'   # 设置title
admin.site.index_title = '运维安全后台'
admin.site.register(models.IdcScan,Idc)
admin.site.register(models.Active_ip,Agent)
admin.site.register(models.process_whitelist,process_list)
admin.site.register(models.ipaddress_blacklist,ipaddress_blacklist)
admin.site.register(models.outgonging_detection,outgonging_detection)
admin.site.register(models.project_info,ProjectInfo)
admin.site.register(models.change_file,ChangeFile)
admin.site.register(models.cron_info,Cron)
admin.site.register(models.expnetwork_info,Expnetwork)



