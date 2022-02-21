from web import views
from django.urls import path


urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('system/aserviceIp/monitor/', views.test_ajax)
]