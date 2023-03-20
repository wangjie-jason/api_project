# Generated by Django 3.2.13 on 2022-08-21 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0027_db_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='DB_monitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('project_id', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('method', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('value', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('status', models.BooleanField(default=False)),
                ('next', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('email', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('robot', models.CharField(blank=True, default='', max_length=100, null=True)),
            ],
        ),
    ]
