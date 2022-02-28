from web import views
from django.urls import path
#调用新增定时计划
from .crontab import scheduler
# from web.views import CssjView
from django.conf.urls import url ##新增


urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('system/aserviceIp/monitor/', views.test_ajax),
    path('index',views.index)
]

