# Generated by Django 3.2.13 on 2022-08-07 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0025_auto_20220807_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='headers',
            field=models.CharField(blank=True, default='[]', max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='params',
            field=models.CharField(blank=True, default='[]', max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='payload_fd',
            field=models.CharField(blank=True, default='[]', max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='payload_xwfu',
            field=models.CharField(blank=True, default='[]', max_length=3000, null=True),
        ),
    ]