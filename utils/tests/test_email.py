import re
import datetime

from django.test import TestCase
from django.core import mail

from profiles.models import TrackTrainsUser
from watcher.models import ByRwTask
from utils.email import send_invitation_email, send_byrw_notification_email


class EmailSendersTest(TestCase):
    def setUp(self):
        self.from_addr = 'user@test.ts'
        self.to_addr = 'guest@test.ts'

        TrackTrainsUser.objects.create_superuser(
            "admin@test.ts",
            "password")

        user = TrackTrainsUser.objects.\
            create_user("user@test.ts", "admin@test.ts", "password")

        self.date_now = datetime.datetime.now().date()

        self.task = ByRwTask()

        self.task.owner = user
        self.task.departure_point = "point1"
        self.task.destination_point = "point2"
        self.task.departure_date = self.date_now
        self.task.train = "trai"
        self.task.car = "VIP"
        self.task.seat = "BS"

        self.task.save()

    def test_invitation_email(self):
        pattern = r"/signup/(.+)/"
        invitation_code = "test12345ee"

        send_invitation_email(self.from_addr, self.to_addr, invitation_code)

        self.assertIsNotNone(mail.outbox)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]

        sres = re.search(pattern, msg.body)

        self.assertIsNotNone(sres)

        token = sres.group(1)

        self.assertIsNotNone(token)
        self.assertEqual(token, invitation_code)

    def test_byrw_notification_email(self):
        send_byrw_notification_email(True, self.task)

        self.assertIsNotNone(mail.outbox)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]

        self.assertTrue("found" in msg.subject)
        self.assertTrue(unicode(self.task.pk) in msg.body)

        cars = dict(ByRwTask.CAR_CHOISES)
        seats = dict(ByRwTask.SEAT_CHOISES)

        str_date_now = self.date_now.strftime("%b. %d, %Y").replace(' 0', ' ')
        self.assertTrue(unicode(str_date_now) in msg.body)
        self.assertTrue(unicode(self.task.departure_point) in msg.body)
        self.assertTrue(unicode(self.task.destination_point) in msg.body)
        self.assertTrue(unicode(self.task.train) in msg.body)
        self.assertTrue(unicode(cars[self.task.car]) in msg.body)
        self.assertTrue(unicode(seats[self.task.seat]) in msg.body)

        send_byrw_notification_email(False, self.task)

        self.assertIsNotNone(mail.outbox)
        self.assertEqual(len(mail.outbox), 2)

        msg = mail.outbox[1]
        self.assertTrue("bought" in msg.subject)
