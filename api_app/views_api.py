from django.shortcuts import render
from api_app.models import *
# Create your views here.
import time
from django.contrib import auth
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import logging
import json
from api_app.views_api_send import SENDAPI
logger = logging.getLogger('django')


# --------------------------  项目内的接口用例模块 视图逻辑层


# 获取接口和配置数据
def get_apis(request):
    project_id = request.GET['project_id']
    apis = list(DB_apis.objects.filter(project_id=project_id).values())
    for i in apis:
        i['children'] = eval(i['children'])
        i['params'] = eval(i['params'])
        try:
            i['headers'] = eval(i['headers'])
        except:
            i['headers'] = []
        i['payload_fd'] = eval(i['payload_fd'])
        i['payload_xwfu'] = eval(i['payload_xwfu'])
    return HttpResponse(json.dumps(apis),content_type='application/json')

# 获取项目的默认选中的接口和配置列表
def get_dck(request):
    project_id = request.GET['project_id']
    dck = DB_project_list.objects.filter(id=project_id)[0].dck.split(',')
    return HttpResponse(json.dumps(dck),content_type='application/json')

# 设置dck
def set_dck(request):
    project_id = request.GET['project_id']
    dck = request.GET['dck']
    DB_project_list.objects.filter(id=project_id).update(dck=dck)
    return get_dck(request)

# 新增空白接口
def add_apis(request):
    project_id = request.GET['project_id']
    new_api = DB_apis.objects.create(project_id=project_id)
    new_api.save()
    return get_apis(request)

# 删除接口或配置
def remove_ac(request):
    id = request.GET['id']
    if '_' in id: #说明删除的是一个二级节点：配置   例如： 3_5   [{},{},{}]
        api_id = id.split('_')[0]
        api = DB_apis.objects.filter(id=api_id)[0]
        children = eval(api.children)
        for i in children:
            if i['id'] == id:
                children.remove(i)
                break
        api.children = str(children)
        api.save()
    else: #说明删除的就是一个一级节点：接口
        DB_apis.objects.filter(id=id).delete()
    return get_apis(request)

# 增加配置
def add_configure(request):
    id=request.GET['id'] #一定是接口的id   []
    api = DB_apis.objects.filter(id=id)[0]
    children = eval(api.children)
    cid = int(children[-1]['id'].split('_')[1])+1 if children else 1
    children.append({"do_time":"after","type":"configure","label":"新配置","method":"","select":"","value":"","id":"%s_%d"%(id,cid)})
    api.children = str(children)
    api.save()
    return get_apis(request)

# 保存配置
def save_configure(request):
    configure = json.loads(request.body.decode('utf-8'))
    api_id = configure['id'].split('_')[0]
    api = DB_apis.objects.filter(id=api_id)[0]
    children = eval(api.children) # [{},{},{}]
    for i in range(len(children)):
        if children[i]['id'] == configure['id']:
            children[i] = configure
            break
    else:
        children.append(configure)
    api.children = str(children)
    api.save()
    return HttpResponse('')

# 上调-配置
def up_configure(request):
    configure_id = request.GET['configure_id']
    api = DB_apis.objects.filter(id=configure_id.split('_')[0])[0]
    children = eval(api.children)
    for i in range(len(children)):
        if children[i]['id'] == configure_id: #找到了
            if i>0:
                children[i],children[i-1] = children[i-1],children[i]
                break
    api.children = str(children)
    api.save()
    return get_apis(request)

# 下降-配置
def down_configure(request):
    configure_id = request.GET['configure_id']
    api = DB_apis.objects.filter(id=configure_id.split('_')[0])[0]
    children = eval(api.children)
    for i in range(len(children)):
        if children[i]['id'] == configure_id:  # 找到了
            if i < len(children)-1:
                children[i], children[i + 1] = children[i + 1], children[i]
                break
    api.children = str(children)
    api.save()
    return get_apis(request)


# 上调-接口
def up_api(request):
    api_id = int(request.GET['api_id'])
    project_id =request.GET['project_id']
    all_api = DB_apis.objects.filter(project_id=project_id)
    for i in range(len(all_api)):
        if all_api[i].id == api_id:# 找到了
            if i>0:
                all_api[i].id,all_api[i-1].id = all_api[i-1].id,all_api[i].id

                children = eval(all_api[i].children)
                for j in range(len(children)):
                    old_cid = children[j]['id'].split('_')[1]
                    children[j]['id'] = '%d_%s'%(all_api[i].id,old_cid)
                all_api[i].children = str(children)

                children = eval(all_api[i-1].children)
                for j in range(len(children)):
                    old_cid = children[j]['id'].split('_')[1]
                    children[j]['id'] = '%d_%s' % (all_api[i-1].id, old_cid)
                all_api[i-1].children = str(children)

                all_api[i].save()
                all_api[i-1].save()
                break
    return get_apis(request)


# 下降-接口
def down_api(request):
    api_id = int(request.GET['api_id'])
    project_id = request.GET['project_id']
    all_api = DB_apis.objects.filter(project_id=project_id)
    for i in range(len(all_api)):
        if all_api[i].id == api_id:  # 找到了
            if i < len(all_api)-1:
                all_api[i].id, all_api[i + 1].id = all_api[i + 1].id, all_api[i].id

                children = eval(all_api[i].children)
                for j in range(len(children)):
                    old_cid = children[j]['id'].split('_')[1]
                    children[j]['id'] = '%d_%s' % (all_api[i].id, old_cid)
                all_api[i].children = str(children)

                children = eval(all_api[i + 1].children)
                for j in range(len(children)):
                    old_cid = children[j]['id'].split('_')[1]
                    children[j]['id'] = '%d_%s' % (all_api[i + 1].id, old_cid)
                all_api[i + 1].children = str(children)

                all_api[i].save()
                all_api[i + 1].save()
                break
    return get_apis(request)


# 保存接口
def save_api(request):
    api = json.loads(request.body.decode('utf-8'))
    DB_apis.objects.filter(id=api['id']).update(**api)
    return get_apis(request)

# 请求接口
def send_api(request):
    api = json.loads(request.body.decode('utf-8'))
    project_id = request.GET['project_id']
    s = SENDAPI(api,{},api['children'])
    response_data = s.index()
    return HttpResponse(json.dumps(response_data),content_type='application/json')

# 上传binary文件
def upload_binary_file(request):
    ApiID = request.GET['ApiID']
    file = request.FILES.get('binary_file',None)
    file_name = '%s_%s'%(ApiID,file)
    fp = open('api_app/static/tmp/'+file_name,'wb+')
    for i in file.chunks():
        fp.write(i)
    fp.close()
    DB_apis.objects.filter(id=int(ApiID)).update(payload_binary=file_name)
    return HttpResponse('')

# 上传fd文件
def upload_fd_file(request):
    ApiID = request.GET['ApiID']
    file = request.FILES.get('fd_file', None)
    file_name = '%s_%s' % (ApiID, file)
    fp = open('api_app/static/tmp/' + file_name, 'wb+')
    for i in file.chunks():
        fp.write(i)
    fp.close()
    return HttpResponse('')

# 获取可用变量
def get_useable_par(request):
    api_id = request.GET['api_id']
    project_id = request.GET['project_id']
    res = ''
    apis = DB_apis.objects.filter(project_id=project_id,id__lt=int(api_id))

    for i in apis:
        children = eval(i.children)
        for j in children:
            if j['method'] == '提取':
                res += '【%s】: '%i.label + j['value'] + '\n'

    return HttpResponse(res)


# 获取正在执行的接口名
def doing_api(request):
    project_id = request.GET['project_id']
    doing_api = DB_project_list.objects.filter(id=int(project_id))[0].doing_api
    return HttpResponse(doing_api)

# 运行大用例
def run(request='',project_id=''):
    if request:
        project_id = request.GET['project_id']
    dck = DB_project_list.objects.filter(id=int(project_id))[0].dck.split(',')
    TQ = {}
    # 生成新的报告
    report = DB_report.objects.create()
    report.project_id = project_id
    report.ctime = time.strftime("%Y-%m-%d %H:%M:%S")
    apis_result = []
    for i in range(len(dck)):
        if dck[i] and '_' not in dck[i]: #证明这个是接口
            need_children = []
            for j in range(i+1,len(dck)):
                if '%s_'%dck[i] in dck[j]:
                    need_children.append(dck[j])
                else:
                    break
            # 实际去请求该接口了
            api = DB_apis.objects.filter(id=int(dck[i])).values()[0] #api此时是个字典
            DB_project_list.objects.filter(id=int(project_id)).update(doing_api=api['label'])
            api['children'] = eval(api['children'])
            children = []
            for c in api['children']:
                if c['id'] in need_children:
                    children.append(c)
            api['params'] = eval(api['params'])
            api['headers'] = eval(api['headers'])
            api['payload_fd'] = eval(api['payload_fd'])
            api['payload_xwfu'] = eval(api['payload_xwfu'])
            # 调用类执行了
            s = SENDAPI(api,TQ,children)
            response_data = s.index()
            TQ = response_data['TQ']
            apis_result.append(response_data['REPORT'])
            if response_data['REPORT']['result'] == False:
                report.all_result = False
    report.apis_result = str(apis_result)
    report.save()
    # 统计
    try:
        old = DB_run_counts.objects.filter(user_id=request.user.id)[0]
        old.RunCase_count += 1
        old.save()
    except:
        pass

    return HttpResponse(str(report.all_result))

# 清空所有报告
def clear_all_reports(request):
    project_id = request.GET['project_id']
    DB_report.objects.filter(project_id = project_id).delete()
    return HttpResponse('')

# 获取所有报告
def get_all_reports(request):
    project_id = request.GET['project_id']
    all_reports = list(DB_report.objects.filter(project_id = project_id).values())[::-1]
    for report in all_reports:
        report['apis_result'] = eval(report['apis_result'])
    return HttpResponse(json.dumps(all_reports),content_type='application/json')


def test_A(request):
    print('A被调用')
    return HttpResponse(json.dumps({"a":111,"b":{"c":11}}),content_type='application/json')



def test_B(request):
    print('B被调用')
    return HttpResponse(json.dumps({"a":222,"b":{"c":22}}),content_type='application/json')