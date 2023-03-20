import json
import threading
import django
import sys, os

sys.path.append('/Users/wangzijia/Downloads/peixun_project/api_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project/settings.py')
django.setup()
from api_app.models import *


def request(flow):
    '任何一个请求经过的时候，都会自动运行该函数'

    params = []
    if '?' in flow.request.url:
        for i in flow.request.url.split('?')[1].split('&'):  # i 是 a=1  或者 b=2
            params.append({'key': i.split('=')[0], 'value': i.split('=')[1]})

    headers = []
    for i in flow.request.headers:  # 是一个字典
        headers.append({'key': i, 'value': str(flow.request.headers[i])})

    form_data = {
        'path': '/' + '/'.join(flow.request.url.split('/')[3:]).split('?')[0],
        'des': '抓包导入的接口',
        'type': 'api',
        'children': '[]',
        'host': '/'.join(flow.request.url.split('/')[:3]),
        'method': flow.request.method,
        'params': str(params),
        'headers': str(headers)
    }
    form_data['label'] = form_data['path']

    if flow.request.method.lower() in ['post', 'put']:
        if 'x-www' in flow.request.headers['Content-Type']:
            form_data['payload_method'] = 'x-www-form-urlencoded'
            tmp = []
            d = flow.request.urlencoded_form
            for i in d.keys():
                tmp.append({'key': i, 'value': d.get(i, '报错')})
            form_data['payload_xwfu'] = str(tmp)

        elif 'form-data' in flow.request.headers['Content-Type']:
            form_data['payload_method'] = 'form-data'
            tmp = []
            d = flow.request.multipart_form
            for i in d.keys():
                if i == 'file':
                    tmp.append({'key': i, 'value': '手动上传文件'})
                else:
                    tmp.append({'key': i, 'value': d.get(i, '报错')})
            form_data['payload_fd'] = str(tmp)

        elif 'plain' in flow.request.headers['Content-Type']:
            form_data['payload_method'] = 'raw'
            form_data['payload_raw_method'] = 'Text'
            form_data['payload_raw'] = str(flow.request.content)


        elif 'javascript' in flow.request.headers['Content-Type']:
            form_data['payload_method'] = 'raw'
            form_data['payload_raw_method'] = 'JavaScript'
            form_data['payload_raw'] = str(flow.request.content)

        elif 'json' in flow.request.headers['Content-Type']:
            if 'query' in flow.request.content:
                form_data['payload_method'] = 'GraphQL'
                form_data['payload_GQL_q'] = json.loads(flow.request.content)['query']
                form_data['payload_GQL_g'] = json.loads(flow.request.content)['variables', '']
            else:
                form_data['payload_method'] = 'raw'
                form_data['payload_raw_method'] = 'JSON'
                form_data['payload_raw'] = str(flow.request.content)

        elif 'xml' in flow.request.headers['Content-Type']:
            form_data['payload_method'] = 'raw'
            form_data['payload_raw_method'] = 'XML'
            form_data['payload_raw'] = str(flow.request.content)

        elif 'html' in flow.request.headers['Content-Type']:
            form_data['payload_method'] = 'raw'
            form_data['payload_raw_method'] = 'HTML'
            form_data['payload_raw'] = str(flow.request.content)
        else:
            form_data['payload_method'] = 'binary'

    t = threading.Thread(target=ttt, args=[form_data, ])
    t.setDaemon(True)
    t.start()


def ttt(form_data):
    '要把所有流经的数据放到数据库中'
    projects = DB_project_list.objects.filter(catch_status=True)
    for project in projects:
        form_data['project_id'] = project.id
        DB_apis.objects.create(**form_data)

        # 统计
        old = DB_run_counts.objects.filter(user_id=str(project.creater))[0]
        old.Import_count += 1
        old.save()


'''
http.HTTPFlow 实例 flow
flow.request.headers #获取所有头信息，包含Host、User-Agent、Content-type等字段
flow.request.url #完整的请求地址，包含域名及请求参数，但是不包含放在body里面的请求参数
flow.request.pretty_url #同flow.request.url目前没看出什么差别
flow.request.host #域名
flow.request.method #请求方式。POST、GET等
flow.request.scheme #什么请求 ，如https
flow.request.path # 请求的路径，url除域名之外的内容
flow.request.get_text() #请求中body内容，有一些http会把请求参数放在body里面，那么可通过此方法获取，返回字典类型
flow.request.query #返回MultiDictView类型的数据，url直接带的键值参数
flow.request.get_content()#bytes,结果如flow.request.get_text()
flow.request.raw_content #bytes,结果如flow.request.get_content()
flow.request.urlencoded_form #MultiDictView，content-type：application/x-www-form-urlencoded时的请求参数，不包含url直接带的键值参数
flow.request.multipart_form #MultiDictView，content-type：multipart/form-data
时的请求参数，不包含url直接带的键值参数

以上均为获取request信息的一些常用方法，对于response，同理
flow.response.status_code #状态码
flow.response.text#返回内容，已解码
flow.response.content #返回内容，二进制
flow.response.setText()#修改返回内容，不需要转码
'''
