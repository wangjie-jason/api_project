# Generated by Django 3.2.13 on 2022-07-16 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0017_alter_db_project_list_dck'),
    ]

    operations = [
        migrations.AddField(
            model_name='db_apis',
            name='disabled',
            field=models.BooleanField(default=True),
        ),
    ]
