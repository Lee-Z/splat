from django.db import models
from django.utils.html import format_html

# Create your models here.
class IdcScan(models.Model):
    idc_id = models.AutoField("序列号",primary_key=True)
#    idc_ip = models.GenericIPAddressField("ip 地址")
    idc_ip = models.CharField("ip 地址",max_length=2000)
    idc_command = models.CharField("命令",max_length=2000)
#    idc_status = models.IntegerField("状态码")
    idc_status = models.BooleanField('是否在白名单',choices=((0,'是'),(1,'否')))
    idc_time = models.DateTimeField("扫描时间",auto_now_add=True)
    idc_value = models.CharField("进程",max_length=2000)
    class Meta:
        # managed = False
        db_table = 'idc_scan'
#        verbose_name = "服务器扫描"
        verbose_name_plural = '服务器扫描'

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
#        return format_html(btn_str, '/pass_audit/?{}'.format(parameter_str))
        return format_html(btn_str,'/dashboard')
    pass_audit_str2.short_description = '通过审核'

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

    def pass_audit_str2(self):
        parameter_str = 'id={}&status={}'.format(str(self.id), str(self.status))
        color_code = ''
        btn_str = '<a class="btn btn-xs btn-danger" href="{}">' \
                  '<input name="通过审核"' \
                  'type="button" id="passButton" ' \
                  'title="审核" value="通过审核">' \
                  '</a>'
        # btn_str = '<a class="btn btn-xs btn-danger" href="{}">' \
        #           '<input name="审核"' \
        #           'type="button" id="passButton" ' \
        #           'btn.disabled ture' \
        #           'title="审核" value="编辑">' \
        #           '</a>' \
        #           '<a class="btn btn-xs btn-danger" href="{}">' \
        #           '<input name="更新"' \
        #           'type="button" id="update"' \
        #           'title="审核" value="更新">' \
        #           '</a>'
        # btn_test = '<button type="button" class="btn btn-info" name="del">删除</button> ' \
        #            '<button type="button" class="btn btn-info" name="update">更新</button>'


        #        return format_html(btn_str, '/pass_audit/?{}'.format(parameter_str))
        return format_html(btn_str,'/dashboard')
    pass_audit_str2.short_description = '操作'
    pass_audit_str2.admin_order_field = 'status'