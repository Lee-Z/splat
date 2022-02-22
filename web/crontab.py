from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import requests
from web import models

#定时请求客户端状态接口
scheduler = BackgroundScheduler()  # 创建一个调度器对象
scheduler.add_jobstore(DjangoJobStore(), "default")  # 添加一个作业
try:
    # @register_job(scheduler, "interval", seconds=1)用interval方式 每1秒执行一次
#    @register_job(scheduler, 'cron', day_of_week='mon-sun', hour='8', minute='30', second='10', id='delete_stale_data')  # 定时执行：这里定时为周一到周日每天早上8：30执行一次
    @register_job(scheduler, "interval", minutes=1, id="time_task", replace_existing=True, misfire_grace_time=120)
    def time_task():
        """定时的任务逻辑"""

        #res = <QuerySet [{'ip': '172.30.2.1'}, {'ip': '172.30.11.100'}, {'ip': '127.0.0.1'}]>
        res = models.Active_ip.objects.values("ip")
        print(res)
        skipnext = False
        #res 遍历取ip
        for i in res:
            print(i['ip'])
            if skipnext:
                models.Active_ip.objects.filter(ip=i['ip'], status=1).update(status=0)
                print("111")
                skipnext =False
                continue
            try:
            #'http://%s:8092/system/aserviceIp/monitor'%(args.server_ip)
                response = requests.get('http://%s:8280/maintain/jiance'%i['ip'])
                models.Active_ip.objects.filter(ip=i['ip'],status=0).update(status=1)
                # models.Active_ip.objects.filter(ip=i['ip'], status=2).update(status=1)
                # models.Active_ip.objects.update_or_create(defaults={'status': 1}, ip=i['ip'])
                print(response.text)
            except:
                models.Active_ip.objects.filter(ip=i['ip'], status=1).update(status=0)
                print("33333")
                skipnext = True



            # models.Active_ip.objects.update_or_create(defaults={'status': 0}, ip=i['ip'])

    register_events(scheduler)
    scheduler.start()
    # scheduler.remove_job(time_task)  # 移除定时任务
except Exception as e:
    print(e)
    scheduler.shutdown()