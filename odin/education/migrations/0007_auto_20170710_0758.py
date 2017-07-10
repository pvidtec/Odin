# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-10 07:58
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0006_auto_20170707_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgrammingLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=110)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extra_options', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BinaryFileTest',
            fields=[
                ('test_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='education.Test')),
                ('file', models.FileField(upload_to='tests')),
            ],
            bases=('education.test',),
        ),
        migrations.CreateModel(
            name='SourceCodeTest',
            fields=[
                ('test_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='education.Test')),
                ('code', models.TextField(blank=True, null=True)),
            ],
            bases=('education.test',),
        ),
        migrations.AddField(
            model_name='test',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='education.ProgrammingLanguage'),
        ),
        migrations.AddField(
            model_name='test',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='education.Task'),
        ),
    ]
