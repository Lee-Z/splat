from web import views
from django.urls import path
#调用新增定时计划
from .crontab import scheduler
# from web.views import CssjView
from django.conf.urls import url ##新增


urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('system/aserviceIp/monitor/', views.test_ajax),
    path('jsindex',views.index),
    url(r'^bar/$', views.ChartView.as_view(), name='demo'),
    url(r'^index/$', views.IndexView.as_view(), name='demo'),
    url(r'^pie/$', views.ChartView.as_view(), name='demo'),
    url(r'^map/$', views.ChartView.as_view(), name='demo'),
    url(r'^mapUpdate/$', views.ChartView.as_view(), name='demo'),
    url(r'^line/$', views.ChartView.as_view(), name='demo'),
    url(r'^lineUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
    url(r'^geo/$', views.ChartView.as_view(), name='demo'),
    url(r'^geoUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
    url(r'^grid/$', views.ChartView.as_view(), name='demo'),
    url(r'^gridUpdate/$', views.ChartUpdateView.as_view(), name='demo'),
]

