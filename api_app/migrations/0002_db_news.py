# Generated by Django 3.2.13 on 2022-06-11 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DB_news',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user_id', models.IntegerField(default=0)),
                ('to_user_id', models.IntegerField(default=0)),
                ('content', models.CharField(blank=True, default='-', max_length=500, null=True)),
            ],
        ),
    ]
