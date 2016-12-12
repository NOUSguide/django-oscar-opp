# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-09 18:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oscar_opp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ('-date_created',), 'verbose_name': 'Transaction'},
        ),
        migrations.AddField(
            model_name='transaction',
            name='checkout_id',
            field=models.CharField(editable=False, max_length=32, null=True, unique=True),
        ),
    ]