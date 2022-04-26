from django.db import models
from django.utils.html import format_html
from django.http import HttpResponse

import django.utils.timezone as timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
# Create your models here.
#进程扫描表
class IdcScan(models.Model):
    idc_id = models.AutoField("序列号",primary_key=True)
#    idc_ip = models.GenericIPAddressField("ip 地址")
    idc_ip = models.CharField("ip 地址",max_length=2000)
    idc_command = models.CharField("命令",max_length=2000)
#    idc_status = models.IntegerField("状态码")

    idc_status = models.BooleanField('是否在白名单',choices=((0,'否'),(1,'是')))
    idc_time = models.DateTimeField("扫描时间",auto_now_add=True)
    idc_value = models.CharField("进程",max_length=2000)
    class Meta:
        # managed = False
        db_table = 'idc_scan'
#        verbose_name = "服务器扫描"
        verbose_name_plural = '服务器扫描'

    # 控制显示长度，必须在adminx的list_display变量中改为函数名
    def short_detail(self):
        if len(str(self.idc_value)) > 30:
            return '{}...'.format(str(self.idc_value)[0:29])
        else:
            return str(self.idc_value)
    short_detail.allow_tags = True
    short_detail.short_description = '进程'
    short_detail.admin_order_field = 'idc_id'

#右侧添加动作按钮
    def pass_audit_str(self):
        parameter_str = 'idc_id={}&status={}'.format(str(self.idc_id), str(self.idc_status))
        color_code = ''
        btn_str = '<a class="btn btn-xs btn-danger" href="{}">' \
                  '<input name="通过审核"' \
                  'type="button" id="passButton" ' \
                  'title="passButton" value="通过审核">' \
                  '</a>'
        return format_html(btn_str, '/pass_audit/?{}'.format(parameter_str))

    pass_audit_str.short_description = ' '

    def pass_audit_str2(self):
        parameter_str = 'idc_id={}&status={}'.format(str(self.idc_id), str(self.idc_status))
        color_code = ''
        # btn_str = '<a class="btn btn-xs btn-danger" href="{}">' \
        #           '<input name="通过审核"' \
        #           'type="button" id="passButton" ' \
        #           'title="审核" value="通过审核">' \
        #           '</a>'
        btn_str = '<a class="btn btn-xs btn-danger" href="{}">' \
                  '<input name="通过审核"' \
                  'type="button" id="passButton" ' \
                  'btn.disabled ture' \
                  'title="审核" value="通过审核">' \
                  '</a>'
       # return format_html(btn_str, '/pass_audit/?{}'.format(parameter_str))
        return format_html(btn_str,'/dashboard')
    pass_audit_str2.short_description = '通过审核'

    def test2(self,request,):
        if request.method == 'POST':
            print("post")
            is_shoucang = request.POST.get("test1")
            print(is_shoucang)
        else:
            print("get")

            return HttpResponse ("HttpResponse")


#客户端列表 表
class Active_ip(models.Model):
    id = models.AutoField("序列号",primary_key=True)
    ip = models.CharField("服务器ip", max_length=2000)
    state = models.BooleanField('状态', choices=((0, '离线'), (1, '在线')),default=0)
    create_time = models.DateTimeField("创建时间",auto_now_add=True)
    purpose = models.CharField("用途", max_length=2000)
    statusChoices = (
        (0,'离线'),
        (1,'在线'),
        (2,'未注册')
    )
    status = models.IntegerField( choices=statusChoices,verbose_name='状态' , default=0 )
    # 在每列后面添加单个按钮
    # def pass_audit_str2(self):
    #     # parameter_str = 'id={}&status={}'.format(str(self.id), str(self.status))
    #     parameter_str = '{}'.format(str(self.id))
    #     color_code = ''
    #     btn_str = '<a class="btn btn-xs btn-danger" href="{}">' \
    #               '<input name="编辑"' \
    #               'type="button" id="passButton" ' \
    #               'title="编辑" value="编辑">' \
    #               '</a>'
    #     btn_test = '<button type="button" class="btn btn-info" name="del">删除</button> ' \
    #                '<button type="button" class="btn btn-info" name="update">更新</button>'
    #     # btn_test = """<a class="changelink" href="{}">编辑</a>"""
    #
    #     return format_html(btn_str, '/admin/web/active_ip/{}/change/'.format(parameter_str))
    #
    # pass_audit_str2.short_description = '列表'
    # pass_audit_str2.admin_order_field = 'status'
    # pass_audit_str2.allow_tags = True


#进程白名单 表
class process_whitelist(models.Model):
    whitelist_id = models.AutoField("序列号",primary_key=True)
    whitelist_process = models.CharField("进程白名单", max_length=2000)
    whitelist_time = models.DateTimeField("创建时间", auto_now_add=True)
    whitelist_purpose = models.CharField("备注", max_length=2000)

#ip地址黑名单表
class ipaddress_blacklist(models.Model):
    blacklist_id = models.AutoField("序列号",primary_key=True)
    blacklist_ip = models.CharField("异常ip", max_length=2000)
    blacklist_time = models.DateTimeField("创建时间", auto_now_add=True)
    blacklist_purpose = models.CharField("备注", max_length=2000)

#服务器出网检测列表
class outgonging_detection(models.Model):
    outgong_id = models.AutoField("ID",primary_key=True)
    outgong_ip = models.CharField("服务器ip", max_length=2000)
    outgong_addr = models.CharField("地理位置", max_length=2000)
    outgong_connect = models.CharField("ip连接", max_length=2000)
    outgong_port = models.CharField("端口号", max_length=2000)
    outgong_scan_time = models.DateTimeField("扫描时间",auto_now_add=True)
    outgong_purpose = models.CharField("用途", max_length=2000)
    statusChoices = (
        (0,'未知地址'),
        (1,'风险地址'),
        (2,'白名单地址')
    )
    outgong_status = models.IntegerField( choices=statusChoices,verbose_name='状态', default=0 )
    network_choices = (
        (0,'私网'),
        (1,'公网'),
    )
    outgong_network = models.IntegerField( choices=network_choices,verbose_name='公私网', default=0 )
    #0 为本地地址 1为中国  2 为海外地址
    outgong_regionnum = models.CharField("地区",max_length=200,default=0)

#获取文件md5值表
class file_md5(models.Model):
    file_id = models.AutoField("序列号",primary_key=True)
    file_name = models.CharField("文件名称", max_length=2000)
    file_size = models.CharField("大小", max_length=2000)
    file_url = models.CharField("文件路径", max_length=2000)
    file_create = models.DateTimeField("文件创建时间")
    file_createtime = models.DateTimeField("创建时间", auto_now_add=True)
    #1 为增加  2为 修改 3 为删除
    file_stat = models.CharField("文件状态", max_length=200)
    file_filemd5 = models.CharField("MD5", max_length=2000,default=0)
    file_serverip = models.CharField("扫描服务器ip", max_length=2000)
    file_scanpath = models.CharField("扫描文件路径", max_length=2000)

#文件完整性扫描
class project_info(models.Model):
    project_id = models.AutoField("序列号",primary_key=True)
    project_name = models.CharField("项目名称", max_length=2000)
    project_ip = models.CharField("项目IP", max_length=2000)
    project_scanpath = models.CharField("项目扫描地址", max_length=2000)
    project_special = models.CharField("排除文件", max_length=2000)
    project_updatetime = models.DateTimeField("更新时间", auto_now_add=True)
    project_sete = models.CharField("状态", max_length=200)

#异常变动文件表
class change_file(models.Model):
    change_id = models.AutoField("序列号",primary_key=True)
    change_name = models.CharField("项目名称", max_length=2000)
    change_ip = models.CharField("项目IP", max_length=2000)
    change_url = models.CharField("文件路径", max_length=2000)
    change_updatetime = models.DateTimeField("更新时间")
    change_scantime = models.DateTimeField("对比时间",auto_now_add=True)
    # 1 为增加  2为 修改 3 为删除
    ChangeChoices = (
        (1,'增加'),
        (2,'修改'),
        (3,'删除')
    )
    change_state = models.IntegerField(choices=ChangeChoices, verbose_name='文件状态')


scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(DjangoJobStore(), 'default')
#定时任务列表
class cron_info(models.Model):
    cron_name = models.CharField("任务名称", max_length=2000,default=0)
    cron_id = models.AutoField("序列号",primary_key=True)
    cron_ip = models.CharField("服务器IP", max_length=2000)
    cron_task = models.CharField("定时任务", max_length=2000)
    cron_strategy = models.CharField("定时策略", max_length=2000)
    cron_choices = (
        (0, '开启'),
        (1, '关闭'),
    )
    cron_stat = models.IntegerField(choices=cron_choices, verbose_name='状态', default=1)
    cron_purpose = models.CharField("备注", max_length=2000)

class expnetwork_info(models.Model):
    expnetwork_id = models.AutoField("序列号",primary_key=True)
    expnetwork_ip = models.CharField("项目IP", max_length=2000)
    expnetwork_scantime = models.DateTimeField("扫描时间", auto_now_add=True)
    expnetwork_choices = (
        (0, '开通访问'),
        (1, '关闭访问'),
    )
    expnetwork_stat = models.IntegerField(choices=expnetwork_choices, verbose_name='状态', default=1)




