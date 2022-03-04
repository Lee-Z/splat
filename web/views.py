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
from pyecharts.charts import Bar,Pie
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.faker import Faker
from pyecharts.charts import Line
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType



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
a = [("广州", 55), ("北京", 66), ("杭州", 77), ("重庆", 88),("西藏", 88)]
b = [("上海", "北京"), ("广州", "北京"), ("杭州", "北京"), ("重庆", "北京"),("西藏", "北京"),("北京","新疆"),("北京","黑龙江")]
def geo_base() -> Geo:
    c = (
            Geo()
            .add_schema(
                maptype="china",
                itemstyle_opts=opts.ItemStyleOpts(color="#323c48", border_color="#111"),
                label_opts=opts.LabelOpts(is_show=True)
            )
            .add(
                "A",
                a,
                type_=ChartType.EFFECT_SCATTER,
                color="red",

            )
            .add(
                "geo",
                b,
                type_=ChartType.LINES,
                effect_opts=opts.EffectOpts(
                    symbol=SymbolType.ARROW, symbol_size=6, color="blue", brush_type="fill"
                ),
                linestyle_opts=opts.LineStyleOpts(curve=0.2,type_="dashed"),
                itemstyle_opts=opts.ItemStyleOpts(color="blue"),
                is_large=True,
            )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title="Geo-Lines"))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .dump_options_with_quotes()
            )
    return c

class ChartView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(geo_base()))


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

def test(request):
    return HttpResponse("www")