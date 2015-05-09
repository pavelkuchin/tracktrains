# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracktrainsuser',
            name='tasks_limit',
            field=models.PositiveSmallIntegerField(default=4, verbose_name=b"The user's limit of tasks."),
        ),
        migrations.AlterField(
            model_name='tracktrainsuser',
            name='inviter',
            field=models.ForeignKey(verbose_name=b'The person who invited this user.', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tracktrainsuser',
            name='invites_counter',
            field=models.PositiveSmallIntegerField(default=0, verbose_name=b'The number of remaining invitations.'),
        ),
    ]
