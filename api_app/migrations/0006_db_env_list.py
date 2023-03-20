# Generated by Django 3.2.13 on 2022-06-19 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0005_db_project_list_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='DB_env_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(blank=True, default='http://', max_length=100, null=True)),
                ('type', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('des', models.CharField(blank=True, default='', max_length=1000, null=True)),
            ],
        ),
    ]