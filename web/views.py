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
                md5_dic.append(
                    models.file_md5(file_name=temp_key,file_size=temp_value['大小'],file_url=temp_value['路径'],file_create=temp_value['创建时间'],file_filemd5=temp_value['MD5'],file_serverip=serverip,file_scanpath=datapath)
                )
            # else:
            #     print("传入字典不对")
            list_all_dict(temp_value,serverip,datapath) #自我调用实现无限遍历
    models.file_md5.objects.bulk_create(md5_dic)

#获取文件md5值存入数据库
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
nowdate = datetime.datetime.now().date()
def mapdata():
    global g

    f = models.outgonging_detection.objects.filter(outgong_regionnum=1, outgong_id__gt=g,outgong_scan_time__gte=nowdate).values('outgong_addr', 'outgong_id')
    print("++++++++++++++++++++++")
    for i in f:
        print(i['outgong_addr'])
        g = i['outgong_id']
        print(g)
        bisect.insort(k, ('北京', i['outgong_addr']))
    print(k)
    return k


def bardata():
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
        .add(
            "",
            a,
            type_=ChartType.EFFECT_SCATTER,
            color="red",

        )
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

