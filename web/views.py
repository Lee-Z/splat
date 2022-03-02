from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import IdcScan
from web import models
from django.http import HttpResponse
import time,subprocess
import json


def dashboard(request):
    user_count = User.objects.count()
    task_count = IdcScan.objects.count()
    context = { 'user_count': user_count, 'task_count': task_count }
    # return render(request, 'dashboard.html',context)
    return render(request, 'map_world.html', context)
VISIT_RECORD = {}
def test_ajax(request):
    if request.method == "GET":
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")
            pt = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            #新增和更新数据,如有更新，如无创建 (defaults是用来更新的， kwargs是用来查询的)
            # models.Active_ip.objects.update_or_create(defaults={'status': 2},ip=ip)
            # models.Active_ip.objects.filter(ip=ip).update(inset_time=pt)
            models.Active_ip.objects.get_or_create(defaults={'status': 2},ip=ip)
            print("插入数据完成")
        return HttpResponse(ip)
    else:
        return HttpResponse("You just need get method")

def index(request):
    json_receive = json.loads(request.body)
    idc_id = json_receive['idc_id']
    jincheng = models.IdcScan.objects.filter(idc_id=idc_id).values('idc_value')
    print("你点击了%s列"%idc_id)
    #取出对应id的进程
    idc_value = jincheng[0]['idc_value']
    models.process_whitelist.objects.get_or_create(whitelist_process=idc_value)
    print("已添加至白名单")
    models.IdcScan.objects.filter(idc_id=idc_id).update(idc_status=1)
    return HttpResponse(idc_value)


