# Generated by Django 3.2.13 on 2022-08-14 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0026_auto_20220807_2002'),
    ]

    operations = [
        migrations.CreateModel(
            name='DB_report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('ctime', models.CharField(blank=True, default='', max_length=15, null=True)),
                ('all_result', models.BooleanField(default=True)),
                ('apis_result', models.TextField(default='[]')),
            ],
        ),
    ]
