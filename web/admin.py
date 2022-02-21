from django.contrib import admin
from web import models
from django.contrib import messages
from django.http import JsonResponse
from django.utils.html import format_html



class Agent(admin.ModelAdmin):
    list_display = ['id', 'ip','statusColored','create_time', 'purpose']
    search_fields = ['ip', 'state','create_time']
#    list_editable = ['idc_ip','idc_status']
    list_filter = ['create_time']


    def statusColored(self, obj):
        if obj.state == 0:
            return format_html('<span style="color:red">{}</span>', '离线')
        else:
            return format_html('<span style="color:green">{}</span>', '在线')

    statusColored.short_description = "状态"
    #将上面的列可排序（显示和其他列头一样）
    statusColored.admin_order_field = 'state'
# Register your models here.
class Idc(admin.ModelAdmin):
    list_display = ['idc_id', 'idc_ip','idc_command','idc_status', 'idc_time','pass_audit_str','idc_value','pass_audit_str2']
    search_fields = ['idc_status', 'idc_ip','idc_value']
#    list_editable = ['idc_ip','idc_status']
    list_filter = ['idc_time']
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


    actions = ('layer_input',)

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







#登录页面设置
admin.site.site_header = '运维安全平台'  # 设置header
admin.site.site_title = '运维安全后台'   # 设置title
admin.site.index_title = '运维安全后台'
admin.site.register(models.IdcScan,Idc)
admin.site.register(models.Active_ip,Agent)


