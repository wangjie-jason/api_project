from django.contrib import admin
import threading
import time
from api_app.views_api import run
from api_app.views import set_monitor_next
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Register your models here.
from api_app.models import *
import subprocess

admin.site.register(DB_notice)
admin.site.register(DB_news)
admin.site.register(DB_project_list)
admin.site.register(DB_env_list)
admin.site.register(DB_api_shop_list)
admin.site.register(DB_power_list)
admin.site.register(DB_apis)
admin.site.register(DB_report)


######## 监控
def email(adresss, content):
    "发邮件"
    mail_to = adresss.split(',')
    mail_host = 'smtp.qq.com'
    mail_user = '*********@qq.com'  # 发送者邮箱地址
    mail_pass = 'qwjroiqj12j1o2jio'  # smtp授权码

    c = MIMEText(content, 'html', 'utf-8')
    msg = MIMEMultipart('related')
    msg['From'] = mail_user
    msg['To'] = mail_to
    msg['Subject'] = '接口测试平台线上监控报告'
    msg.attach(c)

    try:
        server = smtplib.SMTP()
        server.connect(mail_host, 25)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, mail_to, msg.as_string())
        print('发送邮件成功')
        server.close()
    except:
        print('邮件发送失败')


def robotApi(url, content):
    "机器人消息"
    data = {"msg_type": "text", "content": {"text": content}}
    try:
        re = requests.post(url, data=json.dumps(data))
        print(re.text)
    except:
        print('机器人消息发送报错')


def monitor_thread():
    '巡逻线程'
    while True:
        monitors = DB_monitor.objects.all()
        for monitor in monitors:
            if monitor.status != True:
                continue
            if abs(time.time() - float(monitor.next)) < 60:
                project_id = monitor.project_id
                res = run(request='', project_id=project_id)
                set_monitor_next(monitor, 'sys')
                monitor.save()
                # 判断是否需要发送邮件/机器人消息，根据具体公司的领导要求来做。
                if 'False' in str(res.content):
                    last_report = DB_report.objects.filter(project_id=project_id)
                    last_report = last_report[len(last_report) - 1]
                    r = ''
                    for i in eval(last_report.apis_result):
                        r += '\n' + i['label'] + ' : ' + str(i['result'])
                    content = '【%s】线上监控项目报错！%s ' % (monitor.label, r)
                    email(monitor.email, content)
                    robotApi(monitor.robot, content)


t = threading.Thread(target=monitor_thread)
t.daemon = True
t.start()


######## 抓包
# def mitm_start():
#     cmd = 'nohup mitmdump -p 8889 -s api_app/views_mitm.py'
#     subprocess.call(cmd, shell=True)
#
# m = threading.Thread(target=mitm_start)
# m.daemon = True
# m.start()