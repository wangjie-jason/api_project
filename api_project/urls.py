"""api_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from api_app.views import *
from django.views.generic import TemplateView
from api_app.views_api import *

urlpatterns = [
    # ---------------------------------------------- 权限系统无法管理的接口
    path('admin/', admin.site.urls),
    path('',login),
    path('accounts/login/',login),
    path('login_action/',login_action),
    path('register_action/', register_action),
    # path('index/',TemplateView.as_view(template_name='index.html')),
    path('index/',index),
    path('logout/',logout),
    path('get_apis/',get_apis),
    path('get_dck/',get_dck),
    path('set_dck/',set_dck),
    path('add_apis/',add_apis),
    path('remove_ac/',remove_ac),
    path('add_configure/',add_configure),
    path('save_configure/',save_configure),
    path('up_configure/',up_configure),
    path('down_configure/', down_configure),
    path('up_api/',up_api),
    path('down_api/',down_api),
    path('save_api/',save_api),
    path('send_api/', send_api),
    path('upload_binary_file/',upload_binary_file),
    path('upload_fd_file/', upload_fd_file),
    path('download_api/',download_api),
    path('get_useable_par/',get_useable_par), #获取可用变量
    path('doing_api/',doing_api),#获取正在执行的接口名字
    path('run/',run),# 执行大用例
    path('clear_all_reports/',clear_all_reports),
    path('get_all_reports/',get_all_reports),

    path('get_monitor_list/',get_monitor_list),
    path('add_monitor/',add_monitor),
    path('change_monitor_status/',change_monitor_status),
    path('delete_monitor/',delete_monitor),
    path('save_monitor/',save_monitor),

    path('jx_apiDoc/',jx_apiDoc),
    path('import_api_ad/',import_api_ad),

    path('upload_postman_file/',upload_postman_file),
    path('import_api_postman/',import_api_postman),

    path('change_catch_status/',change_catch_status),
    path('open_catch/',open_catch),
    path('close_catch/', close_catch),

    path('upload_img_file/',upload_img_file),
    path('jx_img/',jx_img),

    path('test_A/', test_A),
    path('test_B/', test_B),

    # ------------------------------------------------ 权限系统可以管理的接口，但不一定监管 （接口path只有一级，且path和函数名必须同名）
    re_path('(?P<path>.+)/',diy_power),




]
