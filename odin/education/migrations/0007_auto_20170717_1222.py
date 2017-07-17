# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-17 12:22
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0006_auto_20170707_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncludedTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('extra_options', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProgrammingLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=110)),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('check_status_location', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.SmallIntegerField(choices=[(0, 'pending'), (1, 'running'), (2, 'ok'), (3, 'not_ok'), (4, 'submitted'), (5, 'missing'), (6, 'submitted_without_grading')], default=6)),
                ('test_output', models.TextField(blank=True, null=True)),
                ('return_code', models.IntegerField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='solutions')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='education.Student')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='education.IncludedTask')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('extra_options', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='education.ProgrammingLanguage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='includedtest',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='education.ProgrammingLanguage'),
        ),
        migrations.AddField(
            model_name='includedtest',
            name='task',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='test', to='education.IncludedTask'),
        ),
        migrations.AddField(
            model_name='includedtest',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='included_tests', to='education.Test'),
        ),
    ]
