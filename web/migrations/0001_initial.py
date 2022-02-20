# Generated by Django 3.1 on 2022-02-19 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IdcScan',
            fields=[
                ('idc_id', models.AutoField(primary_key=True, serialize=False, verbose_name='序列号')),
                ('idc_ip', models.CharField(max_length=2000, verbose_name='ip 地址')),
                ('idc_command', models.CharField(max_length=2000, verbose_name='命令')),
                ('idc_status', models.BooleanField(choices=[(0, '是'), (1, '否')], verbose_name='是否在白名单')),
                ('idc_time', models.DateTimeField(auto_now_add=True, verbose_name='扫描时间')),
                ('idc_value', models.CharField(max_length=2000, verbose_name='进程')),
            ],
            options={
                'verbose_name_plural': '服务器扫描',
                'db_table': 'idc_scan',
            },
        ),
    ]
