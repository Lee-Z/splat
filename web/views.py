from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import IdcScan
from web import models
from django.http import HttpResponse
import time,subprocess
import json
from random import randrange
from rest_framework.views import APIView
from pyecharts.charts import Bar,Pie,Page
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.faker import Faker
from pyecharts.charts import Line
from pyecharts.charts import Geo,Grid,Page,Scatter
from pyecharts.globals import ChartType, SymbolType
from pyecharts.globals import ThemeType
import bisect
from django.db.models import Count
import datetime
import requests
import os
from django.http import FileResponse
from werkzeug.wsgi import FileWrapper
import json
from django.http import JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from web import admin
from IPy import IP
import geoip2.database


def cronpage(request):

    # return render(request, 'dashboard.html',context)
    return render(request, 'cronindex.html')



def dashboard(request):
    user_count = User.objects.count()
    task_count = IdcScan.objects.count()
    context = { 'user_count': user_count, 'task_count': task_count }
    # return render(request, 'dashboard.html',context)
    return render(request, 'dashboard.html', context)
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

def ipblacklist(request):
    json_receive = json.loads(request.body)
    outgongid = json_receive['outgong_id']
    ipconnect = models.outgonging_detection.objects.filter(outgong_id=outgongid).values('outgong_connect')
    print("你点击了%s列"%outgongid)
    #取出对应id的进程
    outgong_connect = ipconnect[0]['outgong_connect']
    models.ipaddress_blacklist.objects.get_or_create(blacklist_ip=outgong_connect)
    print("已添加至黑名单")
    models.outgonging_detection.objects.filter(outgong_id=outgongid).update(outgong_status=1)
    return HttpResponse(outgong_connect)






# 字典镶嵌字典遍历 {a:{b:c,d:e}},并写入数据库
def list_all_dict(dict_a,serverip,datapath):
    md5_dic = list()
    if isinstance(dict_a,dict) : #使用isinstance检测数据类型
        for x in range(len(dict_a)):
            temp_key = list(dict_a.keys())[x]
            temp_value = dict_a[temp_key]
#            print("%s : %s" %(temp_key,temp_value))
            if isinstance(temp_value,dict):
                # print("%s  %s" %(temp_key,temp_value['路径']))
                models.file_md5.objects.filter(file_serverip=serverip ,file_scanpath=datapath).delete()
                md5_dic.append(
                    models.file_md5(file_name=temp_key,file_size=temp_value['大小'],file_url=temp_value['路径'],file_create=temp_value['创建时间'],file_filemd5=temp_value['MD5'],file_serverip=serverip,file_scanpath=datapath)
                )
            # else:
            #     print("传入字典不对")
            list_all_dict(temp_value,serverip,datapath) #自我调用实现无限遍历
    models.file_md5.objects.bulk_create(md5_dic)

#获取文件md5值存入数据库 #文件完整性 获取按钮
def obtain(request):
    print("22222")
    json_receive = json.loads(request.body)
    project_id = json_receive['project_id']
    project_ip = models.project_info.objects.filter(project_id=project_id).values('project_ip')
    project_scanpath = models.project_info.objects.filter(project_id=project_id).values('project_scanpath')
    project_special = models.project_info.objects.filter(project_id=project_id).values('project_special')
    path = project_scanpath[0]['project_scanpath']
    special = project_special[0]['project_special']
    ip = project_ip[0]['project_ip']
    print(json_receive)
    print("你点击了%s"%project_ip[0]['project_ip'])
    headers = {'Content-Type': 'application/json'}
    url = "http://%s:8280/maintain/getMd5files" % (ip)
    new_json = {
        'param': path+'&&&'+'['+special+']',
    }
    res = requests.post(url,params=new_json,headers=headers)
    # print(res.text)
    data_dic = json.loads(res.text)
    list_all_dict(data_dic,ip,path)
    return HttpResponse("200")


#文件完整性 对比按钮
def contrast(request):
    print("点击了MD5比对")
    json_receive = json.loads(request.body)
    project_id = json_receive['project_id']
    project_ip = models.project_info.objects.filter(project_id=project_id).values('project_ip')
    project_scanpath = models.project_info.objects.filter(project_id=project_id).values('project_scanpath')
    project_special = models.project_info.objects.filter(project_id=project_id).values('project_special')
    project_name = models.project_info.objects.filter(project_id=project_id).values('project_name')
    path = project_scanpath[0]['project_scanpath']
    special = project_special[0]['project_special']
    ip = project_ip[0]['project_ip']
    print(json_receive)
    print("你点击了%s"%project_ip[0]['project_ip'])
    headers = {'Content-Type': 'application/json'}
    url = "http://%s:8280/maintain/getMd5files" % (ip)
    new_json = {
        'param': path+'&&&'+'['+special+']',
    }
    res = requests.post(url,params=new_json,headers=headers)
    # print(res.text)
    data_dic = json.loads(res.text)
    dbfile = []
    scanfile = []
    isip = models.file_md5.objects.filter(file_serverip=ip).all()
    if isip:
        print("ippand 不为空")
        # 查询数据库中所有文件
        allfile = models.file_md5.objects.values('file_url')
        for i in allfile:
            dbfile.append(i['file_url'])
        if isinstance(data_dic, dict):  # 使用isinstance检测数据类型
            for x in range(len(data_dic)):
                # global scanfile
                temp_key = list(data_dic.keys())[x]
                temp_value = data_dic[temp_key]
                scanfile.append(temp_value['路径'])
                ispath = models.file_md5.objects.filter(file_url=temp_value['路径']).all()
                if ispath:
                    print("文件存在")
                    ismd5 = models.file_md5.objects.filter(file_filemd5=temp_value['MD5']).all()
                    if ismd5:
                        print("文件正常")
                    else:
                        print("文件被修改 %s" % temp_value['路径'])
                        models.change_file.objects.create(change_name=project_name, change_ip=project_ip,
                                                          change_url=temp_value['路径'], change_state='2',change_updatetime=temp_value['创建时间'])
                        headers = {'Content-Type': 'application/json',
                                   'fileName': temp_value['路径']
                                   }
                        url = "http://%s:8280/maintain/download" % (project_ip[0]['project_ip'])
                        res = requests.post(url, headers=headers)
                        # print(res.text)
                        #文件名称
                        host_ini = os.path.basename(temp_value['路径'])
                        #获取文件路径
                        directory = os.path.dirname(temp_value['路径'])
                        hostpath = '/Users/app/'
                        print(ip)
                        #存在全路径拼接
                        # allpath = os.path.join(hostpath,ip,directory)
                        allpath = hostpath+ip+directory
                        if not os.path.exists(allpath): os.makedirs(allpath)
                        # filename = 'C:\iso\%s' % host_ini
                        filename = '%s/%s' % (allpath,host_ini)
                        print(filename)
                        with open(filename, 'wb') as file:
                            file.write(res.content)
                else:
                    print("文件为新增 %s" % temp_value['路径'])
                    models.change_file.objects.create(change_name=project_name,change_ip=project_ip,change_url=temp_value['路径'],change_state='1',change_updatetime=temp_value['创建时间'])
                    headers = {'Content-Type': 'application/json',
                               'fileName': temp_value['路径']
                               }
                    url = "http://%s:8280/maintain/download" % (project_ip[0]['project_ip'])
                    res = requests.post(url, headers=headers)
                    # print(res.text)
                    host_ini = os.path.basename(temp_value['路径'])
                    print(host_ini)
                    filename = 'C:\iso\%s' % host_ini
                    with open(filename, 'wb') as file:
                        file.write(res.content)
        #将数据库文件 与 扫描出来的文件相减
        dbfile = [i for i in dbfile if i not in scanfile]
        for file in dbfile:
            models.change_file.objects.create(change_name=project_name, change_ip=project_ip,
                                              change_url=file, change_state='3',change_updatetime=temp_value['创建时间'])
    else:
        print("该ip未扫描")
    return HttpResponse("200")


#异常文件下载
def download(request):
    change_id = request.GET.get('change_id')
    # models.change_file.objects.filter(change_id=change_id).values(change_url)
    # file_name = os.path.basename(file_path)
    path_file_name = models.change_file.objects.filter(change_id=change_id).values('change_url')
    file_name = os.path.basename(path_file_name[0]['change_url'])
    path_name = path_file_name[0]['change_url']
    db_ip = models.change_file.objects.filter(change_id=change_id).values('change_ip')
    ip = db_ip[0]['change_ip']
    #/opt/msyd_scan/server/download 生产路径
    # file_path = 'C:/iso/%s' % file_name
    all_path = '/Users/app/%s/%s' % (ip,path_name)
    # if not os.path.isfile(file_path):  # 判断下载文件是否存在
    #     return HttpResponse("Sorry but Not Found the File")
    file = open(all_path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=%s' %(file_name)
    return response





#map setting
def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response

def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error

city = ["北京", "上海", "江西", "湖南", "浙江", "江苏","新疆","西藏","河北"]
value = [23, 59, 113, 97, 65, 30, 141,500,1000]
# def map_base() -> Map:
#     c = (
#             Map()
#             # .add("商家A", [list(z) for z in zip(city, value)], "china")
#             .add("",[list(z) for z in zip(city, value)], "china")
#             .set_global_opts(
#                 title_opts=opts.TitleOpts(title="Map-VisualMap（连续型）"),
#                 visualmap_opts=opts.VisualMapOpts(max_=200),
#             )
#             .dump_options_with_quotes()
#         )
#     return c

#单地图
a = [("广州", 55), ("北京", 66), ("杭州", 77), ("重庆", 88),("西藏", 88)]
b = [('上海', '北京'), ('广州', '北京市'), ("杭州", "北京"), ("重庆", "北京"),("西藏", "北京"),("北京","新疆"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","黑龙江"),("北京","河南省周口市"),("北京","濮阳"),("北京","山西省大同市"),]
# def geo_base() -> Geo:
#     c = (
#             Geo()
#             .add_schema(
#                 maptype="china",
#                 itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111"),
#                 label_opts=opts.LabelOpts(is_show=True)
#             )
#             .add(
#                 "A",
#                 a,
#                 type_=ChartType.EFFECT_SCATTER,
#                 color="red",
#
#             )
#             .add(
#                 "geo",
#                 b,
#                 type_=ChartType.LINES,
#                 effect_opts=opts.EffectOpts(
#                     symbol=SymbolType.ARROW, symbol_size=6, color="blue", brush_type="fill"
#                 ),
#                 linestyle_opts=opts.LineStyleOpts(curve=0.2,type_="dashed"),
#                 itemstyle_opts=opts.ItemStyleOpts(color="blue"),
#                 is_large=True,
#             )
#             .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#             .set_global_opts(title_opts=opts.TitleOpts(title="Geo-Lines"))
#             .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#             .dump_options_with_quotes()
#             )
#     return c


'''
四图显示在一个页面，组合
'''
# def grid_vertical() -> Grid:    # 垂直网格
#     bar = (
#         Bar()
#         .add_xaxis(Faker.choose())
#         .add_yaxis("商家A", Faker.values())
#         .add_yaxis("商家B", Faker.values())
#         .set_global_opts(
#             title_opts=opts.TitleOpts(title="Grid-Bar"),
#             legend_opts=opts.LegendOpts(pos_left="20%")
#         )
#     )
#     line = (
#         Line()
#         .add_xaxis(Faker.choose())
#         .add_yaxis("商家A", Faker.values())
#         .add_yaxis("商家B", Faker.values())
#         .set_global_opts(
#             title_opts=opts.TitleOpts(title="Grid-Line", pos_top="48%"),
#             legend_opts=opts.LegendOpts(pos_top="48%", pos_left="20%")
#         )
#     )
#
#     scatter = (
#         Scatter()
#         .add_xaxis(Faker.choose())
#         .add_yaxis("商家A", Faker.values())
#         .add_yaxis("商家B", Faker.values())
#         .set_global_opts(
#             title_opts=opts.TitleOpts(title="Grid-Scatter", pos_right="5%"),
#             legend_opts=opts.LegendOpts(pos_right="25%"),
#         )
#     )
#     line2 = (
#         Line()
#         .add_xaxis(Faker.choose())
#         .add_yaxis("商家A", Faker.values())
#         .add_yaxis("商家B", Faker.values())
#         .set_global_opts(
#             title_opts=opts.TitleOpts(title="Grid-Line2", pos_right="5%", pos_top="48%"),
#             legend_opts=opts.LegendOpts(pos_right="25%", pos_top="48%"),
#         )
#     )
#     grid = (
#         Grid()      # 上下图和左右图
#         .add(chart=bar, grid_opts=opts.GridOpts(pos_bottom="60%", width="38%"))
#         .add(chart=line, grid_opts=opts.GridOpts(pos_top="60%", width="38%"))
#         .add(chart=scatter, grid_opts=opts.GridOpts(pos_left="55%", pos_bottom="60%"))
#         .add(chart=line2, grid_opts=opts.GridOpts(pos_left="55%", pos_top="60%"))
#         # 获取全局 options，JSON 格式（JsCode 生成的函数带引号，在前后端分离传输数据时使用）
#         .dump_options_with_quotes()     # 官方解释：保留 JS 方法引号
#     )
#     return grid

'''
两图组合
'''
c = [1420, 94, 86, 107, 33, 48, 134,22]
d = ["新疆", "黑龙江", "四川", "广东", "吉林", "西藏", "海南","北京"]
g = int()
k = []
def mapdata():
    global g
    nowdate = datetime.datetime.now().date()
    f = models.outgonging_detection.objects.filter(outgong_regionnum=1, outgong_id__gt=g,outgong_scan_time__gte=nowdate).values('outgong_addr', 'outgong_id')
    # print("++++++++++++++++++++++")
    for i in f:
        print(i['outgong_addr'])
        g = i['outgong_id']
        print(g)
        bisect.insort(k, ('北京', i['outgong_addr']))
    print(k)
    return k


def bardata():
    nowdate = datetime.datetime.now().date()
    #select outgong_addr,count(outgong_addr) as outcount from web_outgonging_detection group by outgong_addr;
    objs = models.outgonging_detection.objects.values('outgong_addr').filter(outgong_network=1,outgong_scan_time__gte=nowdate).annotate(
        outcount=Count('outgong_addr'))
    print(objs)
    addres = []
    addressnum = []
    # 这个是否返回的是一组字典对象
    for obj in objs:
        addres.append(obj.get('outgong_addr'))
        addressnum.append(obj.get('outcount'))
        # print(addres, addressnum)
    return addres,addressnum

def grid_vertical() -> Grid:
    geo = (
        Geo()
        .add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111"),
            label_opts=opts.LabelOpts(is_show=True),
            is_roam=False,
            # legend_opts=opts.LegendOpts(pos_left="80%")
        )
        # .add(
        #     "",
        #     a,
        #     type_=ChartType.EFFECT_SCATTER,
        #     # color="red",
        #     color="#6aa84f",
        # )
        .add(
            "",
            mapdata(),
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW,
                symbol_size=6,
                color="#6aa84f",
                brush_type="fill",
            ),
            linestyle_opts=opts.LineStyleOpts(curve=0.2,type_="dashed",color="#6aa84f"),
            itemstyle_opts=opts.ItemStyleOpts(color="red"),
            is_large=True,
            color="red"

        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="地址访问动态图",pos_left="50%",pos_top="5%"),
            # legend_opts=opts.LegendOpts(pos_left="50%")
        )
    )
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK))
            .add_xaxis(bardata()[0])
            .add_yaxis("",bardata()[1],bar_width="50%",category_gap=100)
            # .add_yaxis("商家B", Faker.values())
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            # .set_global_opts(title_opts=opts.TitleOpts(title="Bar-翻转 XY 轴"))
    )

    grid = (
        Grid(
            init_opts=opts.InitOpts(

            )
        )  # 上下图和左右图
            # .add(pie, grid_opts=opts.GridOpts(pos_left="55%", pos_top="60%"))
            .add(bar, grid_opts=opts.GridOpts(pos_top="50%", pos_right="75%"))
            .add(geo, grid_opts=opts.GridOpts(pos_right="300%"))
            # 获取全局 options，JSON 格式（JsCode 生成的函数带引号，在前后端分离传输数据时使用）
            .dump_options_with_quotes()  # 官方解释：保留 JS 方法引号
    )
    return grid




class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(grid_vertical()))


cnt = 9


class ChartUpdateView(APIView):
    def get(self, request, *args, **kwargs):
        global cnt
        cnt = cnt + 1
        return JsonResponse({"name": cnt, "value": randrange(0, 100)})

class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        user_count = User.objects.count()
        task_count = IdcScan.objects.count()
        context = {'user_count': user_count, 'task_count': task_count}
        return HttpResponse(content=open("./templates/index.html").read())
        # return render(request, 'index.html', context)

#axios 请求数据测试接口

def Getaxios(request):
    if request.method == 'GET':
        print('axios 请求')
        data = []
        sever_ip = models.Active_ip.objects.filter(status='1').values('ip')
        for i in sever_ip:
            dicdata = {}
            server_id = models.Active_ip.objects.filter(ip=i['ip']).values('id')
            a.append(server_id[0]['id'])
            dicdata['key'] = server_id[0]['id']
            dicdata['label'] = i['ip']
            data.append(dicdata)
        print(a)
        data_json= json.dumps(data)
        print(data_json)
        result = '[{ "key": 1, "label": "172.30.2.1", "disabled": false },{ "key": 2, "label": "172.30.2.2", "disabled": false }]'
        print(type(result))
        return HttpResponse(data_json)



scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(DjangoJobStore(), 'default')
def PostAxios(request):
    if request.method == 'POST':
        # content = json.loads(request.body.decode())
        print("axios 是post请求")
        print(request.POST.get('serverip'))
        print(request.POST.get('taskoptions'))
        print(request.POST.get('cron'))
        print(request.POST.get('status'))
        print(request.POST.get('remarks'))
        print(request.POST.get('startime'))
        # return HttpResponse("post request")
        try:
            start_time = request.POST.get('cron')  # 用户输入的任务开始时间, '10:00:00'
            start_time = start_time.split(' ')
            second = (start_time)[0]
            minute = (start_time)[1]
            hour = (start_time)[2]
            day = (start_time)[3]
            mon = (start_time)[4]
            week = (start_time)[5]
            year = (start_time)[6]
            name = request.POST.get('cronname')
            id = request.POST.get('remarks')
            serverid = request.POST.get('serverip').split(',')
            taskoptions_list = request.POST.get('taskoptions').split(',')
            # s = content['status']  # 接收执行任务的各种参数
            print(start_time)
            # 创建任务
            for x in serverid:
                server_ip = (models.Active_ip.objects.filter(id=x).values_list('ip'))
                for i in taskoptions_list:
                    if (i == '外网访问定时扫描'):
                        scheduler.add_job(port, 'cron', year=year, day_of_week=week, month=mon, day=day, hour=hour, minute=minute, args=[serverid], second=second,id=str(name+i+x)),
                        # for x in serverid:
                        #     server_ip = (models.Active_ip.objects.filter(id=x).values_list('ip'))
                        models.cron_info.objects.create(cron_name=name,cron_ip=server_ip,cron_task=i,cron_strategy=start_time,cron_stat=request.POST.get('status'))
                        if request.POST.get('status') == '1':
                            scheduler.pause_job(str(name+i+x))

                    elif (i == '文件定时扫描'):
                        scheduler.add_job(md5file, 'cron', year=year, day_of_week=week, month=mon, day=day, hour=hour,
                                          minute=minute, args=[serverid], second=second, id=str(name+i+x)),
                        models.cron_info.objects.create(cron_name=name,cron_ip=server_ip,cron_task=i,cron_strategy=start_time,cron_stat=request.POST.get('status'))
                        if request.POST.get('status') == '1':
                            scheduler.pause_job(str(name+i+x))
                    elif (i == '进程定时扫描'):
                        scheduler.add_job(process, 'cron', year=year, day_of_week=week, month=mon, day=day, hour=hour,
                                          minute=minute, args=[serverid], second=second, id=str(name+i+x)),
                        models.cron_info.objects.create(cron_name=name,cron_ip=server_ip,cron_task=i,cron_strategy=start_time,cron_stat=request.POST.get('status'))
                        if request.POST.get('status') == '1':
                            scheduler.pause_job(str(name+i+x))
                    else:
                        print("未选中定时任务选项")
            # job_name.remove()
            # if (id == '888'):
            #     scheduler.remove_job(jobname)
            #注册定时任务
            register_events(scheduler)
            scheduler.start()
            code = '200'
            message = 'success'
        except Exception as e:
            code = '400'
            message = e

        back = {
            'code': code,
            'message': message
        }
        return JsonResponse(json.dumps(back, ensure_ascii=False))
        # return JsonResponse("11111")

#定时调用服务器出外网连接
def port(queryset):
    print("执行了任务计划")
    outgong_dic = list()
    for e in queryset:
        # print(e)
        try:
            pro_ip = (models.Active_ip.objects.filter(id=e).values_list('ip'))
            # print(pro_ip[0][0])
            url = "http://%s:8280/maintain/getIp" % (pro_ip[0][0])
            new_json = {
            }
            res = requests.post(url, json=new_json)

            # 该函数为 字典1个key值对应多个value值改成1个key值对应一个value值
            def itertransfer(mapper):
                for k, values in mapper.items():
                    for v in values:
                        yield (k, v)

            for k, v in itertransfer(res.json()):
                # print(k, v.split(':')[0])
                # ip = IP(v.split(':')[0])
                ip = IP(v.split(':')[0])
                daydate =  datetime.datetime.now().date()
                objs = models.outgonging_detection.objects.filter(outgong_connect=ip,outgong_scan_time__gte=daydate).values('outgong_id')
                if objs:
                    # 端口扫描今天已存在数据库有该ip访问
                    print('为真有值')
                else:
                    # 外网返回：PUBLIC  内网：PRIVATE  127：LOOPBACK
                    if ip.iptype() == 'PRIVATE' or ip.iptype() == 'LOOPBACK':
                        # print("私网地址")
                        outgong_dic.append(
                            models.outgonging_detection(outgong_ip=pro_ip[0][0], outgong_connect=v.split(':')[0],
                                                        outgong_port=v.split(':')[1], outgong_addr="本地地址",
                                                        outgong_scan_time=k, outgong_network=0))
                    elif ip.iptype() == 'PUBLIC':
                        # 根据ip获取地址位置，并插入数据库
                        with geoip2.database.Reader('web/GeoLite2-City.mmdb') as reader:
                            # print(str(ip))
                            response = reader.city(str(ip))
                            if response.country.names['zh-CN'] == '中国':
                                # 省会
                                province = response.subdivisions.most_specific.names['zh-CN']
                                # 城市
                                city = response.city.names['zh-CN']
                                # geographical_position = '{}{}'.format(province,city)
                                geographical_position = '{}'.format(province)
                                outgong_dic.append(
                                    models.outgonging_detection(outgong_ip=pro_ip[0][0],
                                                                outgong_connect=v.split(':')[0],
                                                                outgong_port=v.split(':')[1],
                                                                outgong_addr=geographical_position,
                                                                outgong_scan_time=k, outgong_network=1,
                                                                outgong_regionnum=1))
                            else:
                                province = response.subdivisions.most_specific.name
                                city = response.city.name
                                geographical_position = '{}'.format(response.country.names['zh-CN'])
                                outgong_dic.append(
                                    models.outgonging_detection(outgong_ip=pro_ip[0][0],
                                                                outgong_connect=v.split(':')[0],
                                                                outgong_port=v.split(':')[1],
                                                                outgong_addr=geographical_position,
                                                                outgong_scan_time=k, outgong_network=1,
                                                                outgong_regionnum=2))
                    else:
                        print("未能识别该地址")
                # return pro_ip[0][0]
        except Exception as  f:
            print(f)
    models.outgonging_detection.objects.bulk_create(outgong_dic)


#定时调用文件完整性扫描
def md5file(w):
    print("点击了定时异常扫描选项")
    print(w)

#定时调用服务器进程扫描
def process(queryset):
    skipnext = False
    res_list = list()
    # 遍历取出全选,遍历所有勾选的ip地址
    for e in queryset:
        try:
            pro_ip = (models.Active_ip.objects.filter(id=e).values_list('ip'))
            print(pro_ip[0][0])
            url = "http://%s:8280/maintain/getProcess" % (pro_ip[0][0])
            new_json = {
            }
            res = requests.post(url, json=new_json)
            if res:
                # print(type(res.json()))
                # print(res_list)
                for x in res.json():
                    # 插入数据库
                    # models.IdcScan.objects.create(idc_ip=pro_ip[0][0],idc_command="ps",idc_status='0',idc_value=i)
                    a = models.process_whitelist.objects.filter(whitelist_process=x)
                    if a:
                        # print("添加白名单")
                        res_list.append(
                            models.IdcScan(idc_ip=pro_ip[0][0], idc_command="ps", idc_status='1', idc_value=x))
                    else:
                        res_list.append(
                            models.IdcScan(idc_ip=pro_ip[0][0], idc_command="ps", idc_status='0', idc_value=x))
        except:
            print("未在线")
    models.IdcScan.objects.bulk_create(res_list)



register_events(scheduler)
# scheduler.remove_job('267ca7b905ac47598cd052799b87c555')

# scheduler.start()
# print(scheduler.get_jobs())
# scheduler.remove_job('888')

#暂停任务计划接口
def extnetwork(request):
    if request.method == 'POST':
        print("post 点解出网")
    return HttpResponse("You just need get method")



