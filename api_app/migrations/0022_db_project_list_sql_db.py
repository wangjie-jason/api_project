# Generated by Django 3.2.13 on 2022-08-07 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0021_db_apis_payload_binary'),
    ]

    operations = [
        migrations.AddField(
            model_name='db_project_list',
            name='sql_db',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]
