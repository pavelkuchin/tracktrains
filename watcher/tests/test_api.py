from datetime import date

from tastypie.test import ResourceTestCase

from profiles.models import TrackTrainsUser
from watcher.models import ByRwTask


class TestByRwTaskResource(ResourceTestCase):
    def setUp(self):
        super(TestByRwTaskResource, self).setUp()

        self.super_user_email = u"supertest@test.ts"
        self.super_user_pass = u"test"

        self.user_email = u"test@test.ts"
        self.user_pass = u"test"

        self.list_url = u"/api/v1/byrwtask/"
        self.details_url = u"/api/v1/byrwtask/%d/"

        self.superuser = TrackTrainsUser.objects.create_superuser(
            self.super_user_email,
            self.super_user_pass)

        self.user = TrackTrainsUser.objects.\
            create_user(self.user_email, self.super_user_email, self.user_pass)

        self.task1= ByRwTask()
        self.task1.owner = self.user
        self.task1.train = "67B"
        self.task1.departure_point = "Gomel"
        self.task1.destination_point = "Minsk"
        self.task1.departure_date = date.today()
        self.task1.save()

        self.task2 = ByRwTask()
        self.task2.owner = self.user
        self.task2.train = "67C"
        self.task2.departure_point = "Minsk"
        self.task2.destination_point = "Kiev"
        self.task2.departure_date = date.today()
        self.task2.save()

        self.post_data = {
                "train": "34F",
                "departure_point": "Krakov",
                "destination_point": "Lviv",
                "departure_date": date.today(),
                "car": 1,
                "seat": "T",
                "owner": "/api/v1/user/%d/" % (self.user.pk,)
            }

    def get_credentials(self, superuser=False):
        if superuser:
            return self.create_basic(
                username=self.super_user_email,
                password=self.super_user_pass)
        else:
            return self.create_basic(
                username=self.user_email,
                password=self.user_pass)

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.list_url))

    def test_get_list(self):
        resp = self.api_client.get(
            self.list_url,
            authentication=self.get_credentials()
        )
        self.assertValidJSONResponse(resp)

        obj_list = self.deserialize(resp)

        self.assertEqual(len(obj_list['objects']), 2)

    def test_get_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(
                self.details_url % (self.task1.id,)
            )
        )

    def test_get_detail(self):
        resp = self.api_client.get(
            self.details_url % (self.task1.id,),
            authentication=self.get_credentials()
        )

        self.assertValidJSONResponse(resp)

        self.assertKeys(self.deserialize(resp),
            [
                u"train",
                u"destination_point",
                u"departure_point",
                u"departure_date",
                u"car",
                u"seat",
                u"created",
                u"id",
                u"is_active",
                u"is_successful",
                u"modified",
                u"owner",
                u"resource_uri",
                u"tracked"
            ]
        )

        self.assertEqual(self.deserialize(resp)['train'], self.task1.train)

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post(
            self.list_url,
            data=self.post_data
        ))

    def test_post_list(self):
        old_count = ByRwTask.objects.count()

        self.assertHttpCreated(self.api_client.post(
            self.list_url,
            data=self.post_data,
            authentication=self.get_credentials()
        ))

        self.assertEqual(ByRwTask.objects.count(), old_count + 1)

    def test_put_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.put(
            self.details_url % (self.task1.pk,),
            data={}
        ))

    def test_put_detail(self):
        resp = self.api_client.get(
            self.details_url % (self.task1.pk,),
            authentication=self.get_credentials()
        )
        obj = self.deserialize(resp).copy()

        obj['destination_point'] = "Kiev"

        old_count = ByRwTask.objects.count()

        resp = self.api_client.put(
            self.details_url % (obj['id'],),
            data=obj,
            authentication=self.get_credentials()
        )

        self.assertHttpAccepted(resp)

        new_count = ByRwTask.objects.count()
        self.assertEqual(old_count, new_count)

    def test_delete_detail_unauthorized(self):
        self.assertHttpUnauthorized(
            self.api_client.delete(self.details_url % (self.task1.pk,))
        )

    def test_delete_detail(self):
        old_count = ByRwTask.objects.count()
        self.assertHttpAccepted(
            self.api_client.delete(
                self.details_url % (self.task1.pk,),
                authentication=self.get_credentials()
            )
        )
        new_count = ByRwTask.objects.count()
        self.assertEqual(old_count - 1, new_count)
