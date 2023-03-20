import re
import subprocess

from django.shortcuts import render
from api_app.models import *
# Create your views here.
import time
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import logging
import json
from python_jenkins_monitor.python_jenkins_monitor import get_next_time
import requests
import easyocr
import Levenshtein
import threading

logger = logging.getLogger('django')


def help(request):
    # 日志记录： xxxx 在什么时间 看了帮助页面
    logger.error('%s 刚刚进入了帮助页面' % request.user.username)
    logger.info('%s 刚刚进入了帮助页面' % request.user.username)
    logger.warning('%s 刚刚进入了帮助页面' % request.user.username)

    return render(request, 'help.html')


# 进入登录页面的函数
def login(request, message=''):
    res = {}
    res["notices"] = list(DB_notice.objects.all().values('content'))[::-1][:2]
    res["message"] = message
    return render(request, 'login.html', res)


# 登录功能
def login_action(request):
    time.sleep(0.3)
    ## 获取用户名/密码
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    ## 去数据库进行比对
    user = auth.authenticate(username=username, password=password)
    if user is None:  # 代表用户名/密码错误
        return login(request, '用户名或密码错误')
    else:  # 代表验证成功
        # 登录
        auth.login(request, user)
        request.session['user'] = username
        # 跳转到首页
        return HttpResponseRedirect('/index/')


# 注册功能
def register_action(request):
    time.sleep(1)
    ## 获取用户名/密码
    username = request.GET['username']
    password = request.GET['password']
    ## 去数据库注册
    try:  # 成功注册
        user = User.objects.create_user(username=username, password=password)
        user.save()
        # 登录
        auth.login(request, user)
        request.session['user'] = username
        # 跳转到首页
        return HttpResponseRedirect('/index/')
    except:  # 用户已存在
        return login(request, '用户名已存在')


# 退出功能
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


# 进入vue的首页
@login_required()
def index(request):
    return render(request, 'index.html')


# 获取统计数据
def get_tj_datas(request):
    # 获取用户id
    userID = request.user.id
    tj_datas = {}
    tj_datas["notices"] = list(DB_notice.objects.all().values('content'))[::-1]
    tj_datas["news"] = list(DB_news.objects.filter(to_user_id=userID).values())[::-1]
    for i in tj_datas["news"]:
        from_user_name = get_object_or_404(User, pk=i["from_user_id"]).username
        i["from_user_name"] = from_user_name
        i["content"] = i["content"][:10] + '...' if len(i['content']) > 10 else i['content']

    tj_datas["overview"] = {
        "project_count": len(DB_project_list.objects.all()),
        "case_count": 0,
        "api_count": len(DB_apis.objects.all()),
        "env_count": len(DB_env_list.objects.all()),
        "user_count": len(User.objects.all()),
    }
    tj_datas["monitor"] = {
        "case_pass": 0,
        "api_pass": 0,
        "case_fail": 0
    }
    your_project = DB_project_list.objects.filter(creater=userID)[0]
    last_report = DB_report.objects.filter(project_id=your_project.id).last()
    try:
        l = [i['result'] for i in eval(last_report.apis_result)]
        tj_datas['monitor']['api_pass'] = int(len([j for j in l if j == True]) / len(l) * 100)
    except:
        tj_datas['monitor']['api_pass'] = 0
    tj_datas["contribution"] = {
        "project": int(
            len(DB_project_list.objects.filter(creater=userID)) / tj_datas['overview']['project_count'] * 100),

    }
    tj_datas['contribution']['case'] = tj_datas['contribution']['project']
    person_api = 0
    person_monitor = 0
    for project in DB_project_list.objects.filter(creater=userID):
        person_api += len(DB_apis.objects.filter(project_id=project.id))
        person_monitor += len(DB_monitor.objects.filter(project_id=project.id))
    try:
        tj_datas['contribution']['api'] = int(person_api / tj_datas['overview']['api_count'] * 100)
    except:
        tj_datas['contribution']['api'] = 0
    try:
        tj_datas['contribution']['monitor'] = int(person_monitor / len(DB_monitor.objects.all()) * 100)
    except:
        tj_datas['contribution']['monitor'] = 0

    return HttpResponse(json.dumps(tj_datas), content_type='application/json')


# 获取实时数据
def get_real_time_datas(request):
    userID = request.user.id
    real_time_datas = {
        "ApiShop_count": len(DB_api_shop_list.objects.all()),
        "UnReadNews_count": len(DB_news.objects.filter(to_user_id=userID, read=False)),
    }
    try:
        real_time_datas.update(list(DB_run_counts.objects.filter(user_id=userID).values())[0])
    except:  # 每个用户只会走一次
        DB_run_counts.objects.create(user_id=userID)
        real_time_datas.update(list(DB_run_counts.objects.filter(user_id=userID).values())[0])

    return HttpResponse(json.dumps(real_time_datas), content_type='application/json')


# 获取项目列表数据
def get_project_list(request):
    #
    keys = request.GET.get('keys', None)
    if keys:
        project_list_data = list((DB_project_list.objects.filter(name__contains=keys,
                                                                 deleted=False) | DB_project_list.objects.filter(
            des__contains=keys, deleted=False)).values())[
                            ::-1]  # select * from 表 where name like %keys% or des like %keys% ;
    else:
        project_list_data = list(DB_project_list.objects.filter(deleted=False).values())[::-1]
    # 增加字段 creater_name
    for i in project_list_data:
        try:
            creater_name = get_object_or_404(User, pk=i['creater']).username
        except:
            creater_name = '无人认领'
        i["creater_name"] = creater_name
    return HttpResponse(json.dumps(project_list_data), content_type='application/json')


# 增加项目
def add_project(request):
    uid = request.user.id if request.user.id else 0
    DB_project_list.objects.create(creater=uid)
    return get_project_list(request)


# 删除项目
def delete_project(request):
    logger.warning('%s 删除了平台的一个项目' % request.user.username)
    project_id = request.GET['project_id']
    DB_project_list.objects.filter(id=project_id).update(deleted=True)
    return get_project_list(request)


# 获取单个项目详情
def get_project_detail(request):
    id = request.GET['id']
    form = list(DB_project_list.objects.filter(id=id).values())[0]
    return HttpResponse(json.dumps(form), content_type='application/json')


# 保存项目
def save_project(request):
    form = json.loads(request.body.decode('utf-8'))
    DB_project_list.objects.filter(id=form['id']).update(**form)
    return HttpResponse('', content_type='application/json')


# ----------------------------- 环境管理部分
# 获取环境列表
def get_env_list(request):
    env_list_data = list(DB_env_list.objects.all().values())[::-1]
    return HttpResponse(json.dumps(env_list_data), content_type='application/json')


# 新增环境
def add_env(request):
    form_data = json.loads(request.body.decode('utf-8'))
    DB_env_list.objects.create(**form_data)
    return get_env_list(request)


# 删除环境
def delete_env(request):
    env_id = request.GET['env_id']
    DB_env_list.objects.filter(id=env_id).delete()
    return get_env_list(request)


# --------------------------- 接口商店
# 获取接口列表
def get_api_shop_list(request):
    api_shop_list = list(DB_api_shop_list.objects.all().values())[::-1]
    return HttpResponse(json.dumps(api_shop_list), content_type='application/json')


# 保存接口
def save_api_shop(request):
    form = json.loads(request.body.decode('utf-8'))
    try:  # 说明编辑更新
        DB_api_shop_list.objects.filter(id=form['id']).update(**form)
    except:  # 新增
        DB_api_shop_list.objects.create(**form)
    return get_api_shop_list(request)


# 删除功能
def delete_api_shop(request):
    api_id = request.GET['api_id']
    DB_api_shop_list.objects.filter(id=api_id).delete()
    return get_api_shop_list(request)


# 获取用户信息
def get_user_detail(request):
    form_data = {
        "user_name": request.user.username,
        "password": '********',
        "user_id": request.user.id,
    }
    try:
        form_data['title'] = request.user.first_name
    except:
        form_data['title'] = ''
    return HttpResponse(json.dumps(form_data), content_type='application/json')


# 保存用户信息
def save_user_detail(request):
    form = json.loads(request.body.decode('utf-8'))
    user = User.objects.get(id=request.user.id)
    user.username = form['user_name']
    user.first_name = form['title']
    if form['password'] != '********':
        user.set_password(form['password'])
        # auth.logout(request)
    user.save()
    return HttpResponse('')


# 上传用户头像
def upload_user_avatar(request):
    myFile = request.FILES.get('user_avatar', None)
    user_id = request.user.id
    file_name = 'userImg_' + str(user_id) + '.jpg'
    fp = open('api_app/static/user_avatar/' + file_name, 'wb+')
    for i in myFile.chunks():
        fp.write(i)
    fp.close()
    return HttpResponse('')


# 获取消息接收者用户列表
def get_to_user_list(request):
    res = {}
    to_user_list = list(User.objects.all().values('username', 'id', 'first_name'))
    for i in range(len(to_user_list)):
        to_user_list[i]['value'] = to_user_list[i]['username']
    res['to_user_list'] = to_user_list
    news = DB_news.objects.filter(to_user_id=request.user.id)
    news.update(read=True)
    news = list(news.values())[::-1]
    for i in news:
        from_user_name = get_object_or_404(User, pk=i["from_user_id"]).username
        i["from_user_name"] = from_user_name

    res['news'] = news
    return HttpResponse(json.dumps(res), content_type='application/json')


# 发送个人消息
def send_news(request):
    data = json.loads(request.body.decode('utf-8'))
    to_user_id = data['to_user_id']
    content = data['content']
    from_user_id = request.user.id
    date = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    DB_news.objects.create(to_user_id=to_user_id, content=content, from_user_id=from_user_id, date=date)
    return HttpResponse('')


# 发送公告
def send_notice(request):
    data = json.loads(request.body.decode('utf-8'))
    content = data['content']
    date = str(time.strftime('%Y-%m-%d %H:%M:%S'))
    DB_notice.objects.create(content=content, date=date)
    return HttpResponse('')


# 查看日志
def look_log(request):
    res = {
        "logs": '',
        "error_count": 0,
        "error_lines": [],
        "warning_count": 0,
        "warning_lines": [],
    }
    with open('wqrf.info.log', 'r') as fp:
        L = fp.readlines()[-1000:]

    # 加行号，统计错误行、错误数。警告行，警告数。
    for i in range(len(L)):
        if '[ERROR]' in L[i]:
            res['error_count'] += 1
            res['error_lines'].append(i + 1)
            res['logs'] += str(i + 1) + ' ' + '【错误行】：' + L[i]
        elif '[WARNING]' in L[i]:
            res['warning_count'] += 1
            res['warning_lines'].append(i + 1)
            res['logs'] += str(i + 1) + ' ' + '【警告行】：' + L[i]
        else:
            res['logs'] += str(i + 1) + ' ' + L[i]
    return HttpResponse(json.dumps(res), content_type='application/json')


# 获取权限列表
def get_power_list(request):
    if request.user.id != 1:
        logger.warning('%s 试图进入权限管理模块，已被固定最高级权限拦截！' % request.user.username)
        return HttpResponse(json.dumps({}), content_type='application/json')

    res = {}
    power_list_data = list(DB_power_list.objects.all().values())
    for i in power_list_data:
        i['users'] = eval(i['users'])
    res['power_list_data'] = power_list_data

    all_users = list(User.objects.all().values('id', 'username', 'first_name'))
    for i in all_users:
        i['title'] = i['first_name']
    res['all_users'] = all_users

    all_paths = '和path同名的函数如下：\n ----------------- \n '
    with open('api_app/views.py', 'r') as fp:
        L = fp.readlines()
    for i in L:
        if 'def ' in i:
            if '(request' in i:
                all_paths += i + '\n'
    res['all_paths'] = all_paths
    return HttpResponse(json.dumps(res), content_type='application/json')


# 保存权限
def save_power(request):
    if request.user.id != 1:
        logger.warning('%s 试图进入权限管理模块，已被固定最高级权限拦截！' % request.user.username)
        return HttpResponse(json.dumps({}), content_type='application/json')
    form = json.loads(request.body.decode('utf-8'))
    DB_power_list.objects.filter(id=form['id']).update(**form)
    return get_power_list(request)


# 删除权限
def delete_power(request):
    id = request.GET['id']
    DB_power_list.objects.filter(id=id).delete()
    return get_power_list(request)


# 增加权限
def add_power(request):
    if request.user.id != 1:
        logger.warning('%s 试图进入权限管理模块，已被固定最高级权限拦截！' % request.user.username)
        return HttpResponse(json.dumps({}), content_type='application/json')
    DB_power_list.objects.create()
    return get_power_list(request)


# 自定义特权判定函数
def diy_power(request, path):
    power = DB_power_list.objects.filter(path=path)
    if power:  # 中了权限监管
        user_ids = [i.split('-')[0] for i in eval(power[0].users)]
        if str(request.user.id) in user_ids:
            # 有权限
            r = locals()
            exec('r = %s(request)' % path)
            return r['r']
        else:  # 没权限
            return HttpResponse('没权限')
    else:  # 没中
        return default_power(request, path)


# 自然默认权限判定函数
def default_power(request, path):
    if path == 'delete_project':
        project_id = request.GET['project_id']
        if request.user.id != DB_project_list.objects.filter(id=project_id)[0].creater:
            return HttpResponse('没权限')
    # if path =='':
    #     ...
    #
    # if path =='':
    #     ...
    #
    # if path =='':
    #     ...
    #
    # if path =='':
    #     ...
    if path in ['favicon.ico']:
        return HttpResponse('')

    # 有权限
    r = locals()
    exec('r = %s(request)' % path)
    return r['r']


# 接口商店下载
def download_api(request):
    project_id = request.GET['project_id']
    api_id = request.GET['api_id']
    api = list(DB_api_shop_list.objects.filter(id=int(api_id)).values())[0]
    api['project_id'] = project_id
    del api['id']
    DB_apis.objects.create(**api)

    # 统计
    old = DB_run_counts.objects.filter(user_id=request.user.id)[0]
    old.Import_count += 1
    old.save()

    return HttpResponse('')


# 查询
def get_monitor_list(request):
    monitor_list = list(DB_monitor.objects.all().values())
    for i in monitor_list:
        try:
            i['next_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(i['next'].split('.')[0])))
        except:
            i['next_date'] = ''
    return HttpResponse(json.dumps(monitor_list), content_type='application/json')


# 增加
def add_monitor(request):
    DB_monitor.objects.create()
    return get_monitor_list(request)


# 删除
def delete_monitor(request):
    id = request.GET['id']
    DB_monitor.objects.filter(id=int(id)).delete()
    return get_monitor_list(request)


# 保存
def save_monitor(request):
    form_data = json.loads(request.body.decode('utf-8'))
    monitor = DB_monitor.objects.filter(id=int(form_data['id']))
    del form_data['next_date']
    monitor.update(**form_data)
    monitor.update(status=False)
    return get_monitor_list(request)


# 更改状态
def change_monitor_status(request):
    id = request.GET['id']
    monitor = DB_monitor.objects.filter(id=int(id))[0]
    if monitor.status == True:  # 我要关上
        monitor.status = False
    else:  # 我要打开
        monitor.status = True
        set_monitor_next(monitor, 'human')
    monitor.save()
    return get_monitor_list(request)


# 计算下一次执行时间
def set_monitor_next(monitor, which):
    if monitor.method == '间隔时间':
        if which == 'human':
            monitor.next = time.time() + float(monitor.value) * 60
        else:  # 巡逻线程调用
            monitor.next = float(monitor.next) + float(monitor.value) * 60

    elif monitor.method == '每日定时':
        h = int(monitor.value.split(':')[0])
        m = int(monitor.value.split(':')[1])
        hm = h * 3600 + m * 60
        today_s = int(time.time()) - int(time.time() - time.timezone) % 86400 + hm
        if which == 'human':
            if today_s <= time.time():  # 今天来不及了
                monitor.next = today_s + 86400
            else:
                monitor.next = today_s
        else:  # 巡逻线程
            monitor.next = monitor.next + 86400

    elif monitor.method == 'jenkins语法':
        monitor.next = get_next_time(monitor.value)


# 解析接口文档
def jx_apiDoc(request):
    ad_url = request.GET['ad_url']
    response = requests.get(ad_url)
    # 发送请求，解析
    form_data = {}
    return HttpResponse(json.dumps(form_data), content_type='application/json')


# 导入接口-接口文档
def import_api_ad(request):
    project_id = request.GET['project_id']
    form_data = json.loads(request.body.decode('utf-8'))
    form_data['project_id'] = project_id
    DB_apis.objects.create(**form_data)

    # 统计
    old = DB_run_counts.objects.filter(user_id=request.user.id)[0]
    old.Import_count += 1
    old.save()

    return HttpResponse('')


# postman 文件上传
def upload_postman_file(request):
    myFile = request.FILES.get('postman_file', None)
    file_name = str(myFile)
    fp = open('api_app/static/postmanFile/' + file_name, 'wb+')
    for i in myFile.chunks():
        fp.write(i)
    fp.close()
    return HttpResponse('')


# postman文件导入
def import_api_postman(request):
    project_id = request.GET['project_id']
    file_name = request.GET['file_name']
    with open('api_app/static/postmanFile/' + file_name, 'r') as fp:
        s = fp.read()
    s = json.loads(s)
    item = s['item']

    for i in item:
        # 此时的i 就是一个接口
        form_data = {
            'project_id': project_id,
            'label': i['name'],
            'type': 'api',
            'children': '[]',
            'des': '【%s】postman导入' % s['info']['name'],
            'host': i['request']['url']['protocol'] + '://' + '.'.join(i['request']['url']['host']),
            'path': '/' + '/'.join(i['request']['url']['path']),
            'method': i['request']['method'],
            'params': str(i['request']['url'].get('query', [])),
            'headers': str(i['request']['header']),
            'payload_method': i['request'].get('body', {}).get('mode', ''),
        }
        if i['request']['url'].get('port', None):
            form_data['host'] += ':' + str(i['request']['url']['port'])
        form_data['payload_method'] = form_data['payload_method'].replace('urlencoded',
                                                                          'x-www-form-urlencoded').replace('graphql',
                                                                                                           'GraphQL').replace(
            'formdata', 'form-data')

        if form_data['payload_method'] == 'form-data':
            form_data['payload_fd'] = str(i['request']['body']['formdata'])
        elif form_data['payload_method'] == 'x-www-form-urlencoded':
            form_data['payload_xwfu'] = str(i['request']['body']['urlencoded'])
        elif form_data['payload_method'] == 'GraphQL':
            form_data['payload_GQL_q'] = i['request']['body']['graphql']['query']
            form_data['payload_GQL_g'] = i['request']['body']['graphql']['variables']
        elif form_data['payload_method'] == 'raw':
            form_data['payload_raw'] = i['request']['body']['raw']
            if i['request']['body'].get('options', None):
                form_data['payload_raw_method'] = i['request']['body']['options']['raw']['language']
                form_data['payload_raw_method'] = form_data['payload_raw_method'].replace('javascript',
                                                                                          'JavaScript').replace('json',
                                                                                                                'JSON').replace(
                    'html', 'HTML').replace('xml', 'XML')
            else:
                form_data['payload_raw_method'] = 'Text'
        DB_apis.objects.create(**form_data)

        # 统计
        old = DB_run_counts.objects.filter(user_id=request.user.id)[0]
        old.Import_count += 1
        old.save()

    return HttpResponse('')


# 改变项目是否可抓包导入的状态
def change_catch_status(request):
    project_id = request.GET['project_id']
    project = DB_project_list.objects.filter(id=int(project_id))[0]
    project.catch_status = (project.catch_status == False)
    project.save()
    return get_project_list(request)


# 开启项目抓包功能
def open_catch(request):
    def mitm_start():
        cmd = 'nohup mitmdump -p 8889 -s api_app/views_mitm.py catch=1'
        subprocess.call(cmd, shell=True)

    m = threading.Thread(target=mitm_start)
    m.daemon = True
    m.start()

    return HttpResponse('')


# 关闭项目抓包功能
def close_catch(rquest):
    subprocess.call("kill -9 `ps -ef | grep catch=1 | grep -v 'grep' | awk '{print $2}'`", shell=True)
    return HttpResponse('')


# img文件上传
def upload_img_file(request):
    myFile = request.FILES.get('img_file', None)
    file_name = str(myFile)
    fp = open('api_app/static/imgFile/' + file_name, 'wb+')
    for i in myFile.chunks():
        fp.write(i)
    fp.close()
    return HttpResponse('')


# 解析图片
def jx_img(request):
    file_name = request.GET['file_name']
    form_data = {'des': '图片识别导入'}
    reader = easyocr.Reader(['ch_sim', 'en'])
    L = reader.readtext('api_app/static/imgFile/' + file_name, detail=0)
    print(L)
    ############################ 设计需求锚点 ，默认误差距离为1
    pars = {
        "label": ['接口描述', '接口名字', '接口名称', '接口name'],
        "host": ['HOST', '域名'],
        "method": ['METHOD', '请求方式'],
        "payload_method": ['请求类型', '请求体类型'],
        "path": ['URL', 'url', 'PATH', '路由', '[JFI'],
        "headers": ["headers", "请求头"],
        "params": ['params', 'Params', 'url参数'],
        "参数锚点": ['参数名', '参数列表', '请求体参数']
    }
    ########################## 矫正列表
    news = {
        'multipart/form-data': {'payload_method': 'form-data'},
        'application/x-www-form-urlencoded': {'payload_method': 'x-www-form-urlencoded'},
        'application/json': {'payload_method': 'raw', 'payload_raw_method': 'JSON'},
        'text/xml': {'payload_method': 'raw', 'payload_raw_method': 'XML'},
        'text/html': {'payload_method': 'raw', 'payload_raw_method': 'HTML'},
        'text/plain': {'payload_method': 'raw', 'payload_raw_method': 'Text'},
        'text/javascript': {'payload_method': 'raw', 'payload_raw_method': 'JavaScript'},
    }
    ########################## 参数部分
    payload_index = 0  # 参数起始位置
    payload_step = 5  # 根据公司业务具体情况而定

    def wirte_payload(payload_method):
        if payload_method == 'form_data':
            payload_tmp = []
            for i in range(payload_index, len(L), payload_step):
                payload_tmp.append({'key': L[i]})
            form_data['payload_fd'] = str(payload_tmp)
        elif payload_method == 'x-www-form-urlencoded':
            payload_tmp = []
            for i in range(payload_index, len(L), payload_step):
                payload_tmp.append({'key': L[i]})
            form_data['payload_xwfu'] = str(payload_tmp)
        elif payload_method == 'raw':
            if form_data['payload_raw_method'] == 'JSON':  # 这块算法 根据公司业务规则灵活改变
                payload_tmp = {}
                for i in range(payload_index, len(L), payload_step):
                    payload_tmp[L[i]] = ''
                form_data['payload_raw'] = json.dumps(payload_tmp)

    ########################## 找到这些关键锚点并把能拿的数据都拿出来
    for par in pars.keys():
        max = [0, 0]  # 得分 下标
        for v in pars[par]:
            for l in range(len(L)):  # l 是下标
                score = Levenshtein.ratio(v, L[l])
                if score > max[0] and score > 0.5:  # 具体多少大家根据自己公司业务情况而定
                    max = [score, l]
                if max[0] == 1:  # 如果已经是满分
                    break
            else:
                continue
            break
        if max[0] > 0.5:  # 具体多少大家根据自己公司业务情况而定
            # 找到锚点

            try:
                old = L[max[1] + 1]
                max_n = [0, '']  # 存放最可能得矫正值
                for new in news.keys():
                    score_n = Levenshtein.ratio(new, old)
                    if score_n > max_n[0] and score_n > 0.7:  # 这里具体加多少 自己定。
                        max_n = [score_n, new]
                    if max_n[0] == 1:
                        break
                if max_n[0] > 0.7:  # 证明有货
                    form_data.update(news[max_n[1]])
                else:
                    form_data[par] = old

                ###### 特殊处理部分 ############
                if par == 'url':
                    params = []
                    if '?' in old:
                        for i in old.split('?')[1].split('&'):
                            params.append({'key': i.split('=')[0], 'value': i.spilt('=')[1]})
                    form_data['params'] = str(params)

                if par == '参数锚点':
                    payload_index = max[1] + payload_step
            except:
                pass

    if form_data.get('参数锚点', None):
        ### 写入参数
        wirte_payload(form_data.get('payload_method', None))
        ### 删除参数锚点从form_data
        del form_data['参数锚点']

    return HttpResponse(json.dumps(form_data), content_type='application/json')
