import web.views
from web import views
from django.urls import path
#调用新增定时计划
from .crontab import scheduler
# from web.views import CssjView
from django.conf.urls import url ##新增


urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('cronpage', views.cronpage, name='cronpage'),
    path('connect', views.SshConnect, name='connect'),
    path('addextpage', views.addextpage, name='cronpage'),
    path('system/aserviceIp/monitor/', views.test_ajax),
    path('system/aserviceIp/obtain/', views.obtain),
    path('system/aserviceIp/contrast/', views.contrast),
    path('download', views.download),
    path('jsindex',views.index),
    path('ipblacklist',views.ipblacklist),
    path('extnetwork',views.extnetwork),
    path('getaxios',views.Getaxios),
    path('postaxios',views.PostAxios),
    url(r'^bar/$', views.ChartView.as_view(), name='demo'),
    url(r'^index/$', views.IndexView.as_view(), name='demo'),
    url(r'^pie/$', views.ChartView.as_view(), name='demo'),
    url(r'^pieUpdate/$', views.ChartView.as_view(), name='demo'),
    url(r'^map/$', views.ChartView.as_view(), name='demo'),
    url(r'^mapUpdate/$', views.ChartView.as_view(), name='demo'),
    url(r'^line/$', views.ChartView.as_view(), name='demo'),
    url(r'^lineUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
    url(r'^geo/$', views.ChartView.as_view(), name='demo'),
    url(r'^geoUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
    url(r'^grid/$', views.ChartView.as_view(), name='demo'),
    url(r'^gridUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
    url(r'^page/$', views.ChartView.as_view(), name='demo'),
    url(r'^pageUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
]
handler404 = views.page_not_found

