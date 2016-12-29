# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 08:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import web_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            bases=(web_app.models.MyCommon, models.Model),
        ),
        migrations.CreateModel(
            name='BookInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('version', models.PositiveIntegerField()),
                ('cover', models.ImageField(null=True, upload_to='')),
                ('description', models.TextField(null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('authors', models.ManyToManyField(to='web_app.AuthorInfo')),
            ],
            bases=(web_app.models.MyCommon, models.Model),
        ),
        migrations.CreateModel(
            name='CatalogInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            bases=(web_app.models.MyCommon, models.Model),
        ),
        migrations.CreateModel(
            name='PublisherInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            bases=(web_app.models.MyCommon, models.Model),
        ),
        migrations.AddField(
            model_name='bookinfo',
            name='catalog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_app.CatalogInfo'),
        ),
        migrations.AddField(
            model_name='bookinfo',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_app.PublisherInfo'),
        ),
    ]