from django.db import models

# Create your models here.
class DB_notice(models.Model):
    content = models.CharField(max_length=100,null=True,blank=True,default='')
    date = models.CharField(max_length=50,null=True,blank=True,default='-')
    def __str__(self):
        return self.content

class DB_news(models.Model):
    from_user_id = models.IntegerField(default=0)
    to_user_id = models.IntegerField(default=0)
    content = models.CharField(max_length=500,null=True,blank=True,default='-')
    date = models.CharField(max_length=50,null=True,blank=True,default='-')
    read = models.BooleanField(default=False)
    def __str__(self):
        return self.content[:20]+'...'

class DB_project_list(models.Model):
    name = models.CharField(max_length=50,null=True,blank=True,default='-')
    des = models.CharField(max_length=500,null=True,blank=True,default='-')
    creater = models.IntegerField(default=0)
    private = models.BooleanField(default=False) # 私密项目
    Line = models.CharField(max_length=50,null=True,blank=True,default='') # 业务线: app  web
    deleted = models.BooleanField(default=False) #假删除
    ####
    email_to = models.CharField(max_length=500,null=True,blank=True,default='[]')
    sql_host = models.CharField(max_length=50,null=True,blank=True,default='')
    sql_port = models.IntegerField(default=0)
    sql_user = models.CharField(max_length=50,null=True,blank=True,default='')
    sql_pwd = models.CharField(max_length=50,null=True,blank=True,default='')
    sql_db = models.CharField(max_length=50,null=True,blank=True,default='')
    ####
    doing_api = models.CharField(max_length=50,null=True,blank=True,default='')
    end_result = models.TextField(default='')
    dck = models.CharField(max_length=500,null=True,blank=True,default='')
    ###
    catch_status = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class DB_env_list(models.Model):
    host = models.CharField(max_length=100,null=True,blank=True,default="http://")
    type = models.CharField(max_length=100,null=True,blank=True,default='')
    des = models.CharField(max_length=1000,null=True,blank=True,default='')
    def __str__(self):
        return self.host

class DB_api_shop_list(models.Model):
    label = models.CharField(max_length=100, null=True, blank=True, default='新接口')  # 接口名字
    type = models.CharField(max_length=10, null=True, blank=True, default='api')
    children = models.CharField(max_length=5000, null=True, blank=True, default='[]')
    des = models.CharField(max_length=300, null=True, blank=True, default='')
    host = models.CharField(max_length=300, null=True, blank=True, default='')
    path = models.CharField(max_length=300, null=True, blank=True, default='')
    method = models.CharField(max_length=30, null=True, blank=True, default='')
    params = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    headers = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    payload_method = models.CharField(max_length=30, null=True, blank=True, default='')
    payload_fd = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    payload_xwfu = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    payload_raw_method = models.CharField(max_length=30, null=True, blank=True, default='')
    payload_raw = models.CharField(max_length=3000, null=True, blank=True, default='')
    payload_GQL_q = models.CharField(max_length=3000, null=True, blank=True, default='')
    payload_GQL_g = models.CharField(max_length=3000, null=True, blank=True, default='')
    payload_binary = models.CharField(max_length=100, null=True, blank=True, default='')
    def __str__(self):
        return self.name

class DB_power_list(models.Model):
    name = models.CharField(max_length=50,null=True,blank=True,default='') #名字
    users = models.CharField(max_length=500,null=True,blank=True,default='[]') #所拥有权限的用户
    path = models.CharField(max_length=100,null=True,blank=True,default='') # 监管的路由部分。
    def __str__(self):
        return self.name

class DB_apis(models.Model):
    project_id = models.IntegerField(default=0) # 所属的项目id
    label = models.CharField(max_length=100,null=True,blank=True,default='新接口') # 接口名字
    type = models.CharField(max_length=10,null=True,blank=True,default='api')
    children = models.CharField(max_length=5000,null=True,blank=True,default='[]')
    des = models.CharField(max_length=300,null=True,blank=True,default='')
    host = models.CharField(max_length=300,null=True,blank=True,default='')
    path = models.CharField(max_length=300,null=True,blank=True,default='')
    method = models.CharField(max_length=30,null=True,blank=True,default='')
    params = models.CharField(max_length=3000,null=True,blank=True,default='[]')
    headers = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    payload_method = models.CharField(max_length=30, null=True, blank=True, default='')
    payload_fd = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    payload_xwfu = models.CharField(max_length=3000, null=True, blank=True, default='[]')
    payload_raw_method = models.CharField(max_length=30, null=True, blank=True, default='')
    payload_raw = models.CharField(max_length=3000, null=True, blank=True, default='')
    payload_GQL_q = models.CharField(max_length=3000, null=True, blank=True, default='')
    payload_GQL_g = models.CharField(max_length=3000, null=True, blank=True, default='')
    payload_binary = models.CharField(max_length=100,null=True,blank=True,default='')

    def __str__(self):
            return self.label

class DB_report(models.Model):
    project_id = models.CharField(max_length=10,null=True,blank=True,default='') #所属项目id
    ctime = models.CharField(max_length=15,null=True,blank=True,default='') #
    all_result = models.BooleanField(default=True) #最终结果
    apis_result = models.TextField(default='[]') #详细接口结果
    def __str__(self):
        return self.ctime

class DB_monitor(models.Model):
    label = models.CharField(max_length=100,default='',null=True,blank=True)
    project_id = models.CharField(max_length=10,default='',null=True,blank=True)
    method = models.CharField(max_length=10,default='',null=True,blank=True) # 间隔时间 ， 每日定时，接口触发，jenkins语法
    value  = models.CharField(max_length=100,default='',null=True,blank=True)
    status = models.BooleanField(default=False) #开关状态
    next =  models.CharField(max_length=100,default='',null=True,blank=True)
    email =  models.CharField(max_length=100,default='',null=True,blank=True)
    robot =   models.CharField(max_length=100,default='',null=True,blank=True) #机器人接口 ，钉钉，企业微信，飞书

    def __str__(self):
        return self.label

class DB_run_counts(models.Model):
    user_id = models.CharField(max_length=10,null=True,blank=True,default='')
    RunCase_count = models.IntegerField(default=0)
    Import_count = models.IntegerField(default=0)
    def __str__(self):
        return str(self.user_id)