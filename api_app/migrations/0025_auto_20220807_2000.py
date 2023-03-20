# Generated by Django 3.2.13 on 2022-08-07 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0024_remove_db_api_shop_list_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='headers',
            field=models.CharField(blank=True, default='[{"key":"","value":"","des":""}]', max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='params',
            field=models.CharField(blank=True, default='[{"key":"","value":"","des":""}]', max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='payload_fd',
            field=models.CharField(blank=True, default='[{"key":"","value":"","des":""}]', max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='db_api_shop_list',
            name='payload_xwfu',
            field=models.CharField(blank=True, default='[{"key":"","value":"","des":""}]', max_length=3000, null=True),
        ),
    ]
