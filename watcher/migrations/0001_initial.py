# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ByRwTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'Active for processing')),
                ('is_successful', models.BooleanField(default=False, verbose_name=b'Seat has been found')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('tracked', models.DateTimeField(null=True, verbose_name=b'When the Job has processed the task last time', blank=True)),
                ('departure_point', models.CharField(max_length=255, verbose_name=b'The departure station name')),
                ('destination_point', models.CharField(max_length=255, verbose_name=b'The destination station name')),
                ('departure_date', models.DateField(verbose_name=b'The required departure date')),
                ('train', models.CharField(max_length=5, verbose_name=b'The train short code id', blank=True)),
                ('car', models.CharField(default=b'ANY', max_length=5, verbose_name=b'Preferred train car type', choices=[(b'ANY', b'Any type'), (b'VIP', b'VIP car'), (b'SLE', b'Sleeping car'), (b'COM', b'Compartment car'), (b'RB', b'Reserved-berths car'), (b'RS', b'Car with regular seats'), (b'TC', b'Third-class car')])),
                ('seat', models.CharField(default=b'ANY', max_length=5, verbose_name=b'Preferred train seat', choices=[(b'ANY', b'Any seat'), (b'B', b'Bottom place'), (b'T', b'Top place'), (b'BS', b'Bottom place by side'), (b'TS', b'Top place by side')])),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'By RW Task',
                'verbose_name_plural': 'By RW Tasks',
            },
            bases=(models.Model,),
        ),
    ]
