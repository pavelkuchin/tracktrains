# -*- coding: utf-8 -*-
import datetime

from django.core.management import call_command
from django.test import TestCase

from profiles.models import TrackTrainsUser
from watcher.models import ByRwTask


class JobByRwTrainwayTest(TestCase):
    """
    Test for job_bytrainway.
    !!! Caution, tests can be unstable because 3th party resource is involved
    """
    def setUp(self):
        TrackTrainsUser.objects.create_superuser(
            "admin@test.ts",
            "password")

        self.user = TrackTrainsUser.objects.\
            create_user("user@test.ts", "admin@test.ts", "password")

    def test_case1(self):
        "job have to delete expired tasks"

        exp_task = ByRwTask()
        exp_task.owner = self.user
        exp_task.departure_point = "HOMIEĹ PASAŽYRSKI"
        exp_task.destination_point = "MINSK"
        exp_task.departure_date = datetime.datetime.now()\
            - datetime.timedelta(days=2)
        exp_task.save()

        self.assertEquals(ByRwTask.objects.count(), 1)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        self.assertEquals(ByRwTask.objects.count(), 0)

    def test_case2(self):
        """
        job should be able to find a seat for
        specific direction and date but without other params
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertTrue(task.is_successful)

    def test_case3(self):
        """
        job should be able to find a seat for
        specific direction, date, train name,
        but without other params
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.train = "631Б"
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertTrue(task.is_successful)

    def test_case4(self):
        """
        job should be able to find a seat for
        specific direction, date, train name,
        car type but without other params
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.train = "631Б"
        task.car = "RB"
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertTrue(task.is_successful)

    def test_case5(self):
        """
        job should be able to find a seat for
        specific direction, date, train name,
        car type and seat type
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.train = "631Б"
        task.car = "RB"
        task.seat = "TS"
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertTrue(task.is_successful)

    def test_case6(self):
        """
        job should be able to find a seat for
        specific direction, date and seat type
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.seat = "TS"
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertTrue(task.is_successful)

    def test_case7(self):
        """
        job should be able to find a seat for
        specific direction, date and car type
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.car = "RB"
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertTrue(task.is_successful)

    def test_case8(self):
        """
        if task flag is_active equals false then
        task should be omitted
        """

        task = ByRwTask()
        task.owner = self.user
        task.departure_point = "HOMIEĹ PASAŽYRSKI"
        task.destination_point = "MINSK"
        task.is_active = False
        task.departure_date = datetime.datetime.now()\
            + datetime.timedelta(days=20)
        task.save()

        self.assertFalse(task.is_successful)

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        task = ByRwTask.objects.get(id=task.id)

        self.assertFalse(task.is_successful)
