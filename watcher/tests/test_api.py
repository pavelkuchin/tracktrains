# -*- coding: utf-8 -*-

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

        self.list_url = u"/v1/byrwtask/"
        self.details_url = u"/v1/byrwtask/%d/"

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
                "owner": "/v1/user/%d/" % (self.user.pk,)
            }

    def auth(self, superuser=False):
        if superuser:
            auth_data = {
                'login': self.super_user_email,
                'password': self.super_user_pass
            }
        else:
            auth_data = {
                'login': self.user_email,
                'password': self.user_pass
            }

        login_url = u'/v1/user/login/'

        self.api_client.post(
            login_url,
            data=auth_data
        )

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(self.list_url))

    def test_get_list(self):
        self.auth()
        resp = self.api_client.get(self.list_url)
        self.assertValidJSONResponse(resp)

        obj_list = self.deserialize(resp)

        self.assertEqual(len(obj_list['objects']), 2)

    def test_get_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(
                self.details_url % (self.task1.id,)
            )
        )

    def test_get_detail(self):
        self.auth()

        resp = self.api_client.get(self.details_url % (self.task1.id,))

        self.assertValidJSONResponse(resp)

        data = self.deserialize(resp)

        self.assertKeys(data,
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

        self.assertEqual(data['train'], self.task1.train)

    def test_post_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.post(
            self.list_url,
            data=self.post_data
        ))

    def test_post_list(self):
        self.auth()

        old_count = ByRwTask.objects.count()

        self.assertHttpCreated(self.api_client.post(
            self.list_url,
            data=self.post_data
        ))

        self.assertEqual(ByRwTask.objects.count(), old_count + 1)

    def test_put_detail_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.put(
            self.details_url % (self.task1.pk,),
            data={}
        ))

    def test_put_detail(self):
        self.auth()

        resp = self.api_client.get(self.details_url % (self.task1.pk,))
        obj = self.deserialize(resp).copy()

        obj['destination_point'] = "Kiev"

        old_count = ByRwTask.objects.count()

        resp = self.api_client.put(
            self.details_url % (obj['id'],),
            data=obj
        )

        self.assertHttpAccepted(resp)

        new_count = ByRwTask.objects.count()
        self.assertEqual(old_count, new_count)

    def test_delete_detail_unauthorized(self):
        self.assertHttpUnauthorized(
            self.api_client.delete(self.details_url % (self.task1.pk,))
        )

    def test_delete_detail(self):
        self.auth()

        old_count = ByRwTask.objects.count()
        self.assertHttpAccepted(
            self.api_client.delete(self.details_url % (self.task1.pk,))
        )
        new_count = ByRwTask.objects.count()
        self.assertEqual(old_count - 1, new_count)

class TestByRwTaskResourceAuth(ResourceTestCase):
    def setUp(self):
        super(TestByRwTaskResourceAuth, self).setUp()

        self.super_user_email = u"supertest@test.ts"
        self.super_user_pass = u"test"

        self.user1_email = u"test1@test.ts"
        self.user1_pass = u"test"

        self.user2_email = u"test2@test.ts"
        self.user2_pass = u"test"

        self.list_url = u"/v1/byrwtask/"
        self.details_url = u"/v1/byrwtask/%d/"

        self.superuser = TrackTrainsUser.objects.create_superuser(
            self.super_user_email,
            self.super_user_pass)

        self.user1 = TrackTrainsUser.objects.\
            create_user(self.user1_email, self.super_user_email, self.user1_pass)

        self.user2 = TrackTrainsUser.objects.\
            create_user(self.user2_email, self.super_user_email, self.user2_pass)

        self.task1 = ByRwTask()
        self.task1.owner = self.user1
        self.task1.train = "67B"
        self.task1.departure_point = "Gomel"
        self.task1.destination_point = "Minsk"
        self.task1.departure_date = date.today()
        self.task1.save()

        self.task2 = ByRwTask()
        self.task2.owner = self.user2
        self.task2.train = "67C"
        self.task2.departure_point = "Minsk"
        self.task2.destination_point = "Kiev"
        self.task2.departure_date = date.today()
        self.task2.save()

        self.post_data1 = {
                "train": "34F",
                "departure_point": "Krakov",
                "destination_point": "Lviv",
                "departure_date": date.today(),
                "car": 1,
                "seat": "T",
                "owner": "/v1/user/%d/" % (self.user2.pk,)
            }

        self.post_data2 = {
                "train": "24F",
                "departure_point": "Gomel",
                "destination_point": "London",
                "departure_date": date.today(),
                "car": 1,
                "seat": "T",
                "owner": "/v1/user/%d/" % (self.user2.pk,)
            }

    def auth(self, usernum=1):
        if usernum == 0:
            auth_data = {
                'login': self.super_user_emai,
                'password': self.super_user_pass
            }
        elif usernum == 1:
            auth_data = {
                'login': self.user1_email,
                'password': self.user1_pass
            }
        elif usernum == 2:
            auth_data = {
                'login': self.user2_email,
                'password': self.user2_pass
            }

        self.login_url = u'/v1/user/login/'

        self.api_client.post(
            self.login_url,
            data = auth_data
        )

    def test_get_list(self):
        self.auth(1)
        resp = self.api_client.get(
            self.list_url
        )
        self.assertValidJSONResponse(resp)

        obj_list = self.deserialize(resp)

        self.assertEqual(len(obj_list['objects']), 1)
        self.assertEqual(obj_list['objects'][0]['train'], self.task1.train)

    def test_get_detail(self):
        self.auth(1)
        resp = self.api_client.get(
            self.details_url % (self.task2.pk,)
        )

        self.assertHttpUnauthorized(resp)

    def test_post_item(self):
        self.auth(1)
        self.assertHttpUnauthorized(self.api_client.post(
            self.list_url,
            data=self.post_data1
        ))

    def test_post_list(self):
        self.auth(2)

        old_count = ByRwTask.objects.count()

        self.assertHttpAccepted(self.api_client.patch(
            self.list_url,
            data={"objects":[self.post_data1, self.post_data2]}
        ))

        new_count = ByRwTask.objects.count()

        self.assertEqual(old_count+2, new_count)

    def test_put_detail(self):
        self.auth(1)
        resp = self.api_client.get(
            self.details_url % (self.task1.pk,)
        )
        obj = self.deserialize(resp).copy()

        obj['destination_point'] = "Gomel"

        resp = self.api_client.put(
            self.details_url % (self.task2.pk,),
            data=obj
        )

        self.assertHttpUnauthorized(resp)

        self.assertEqual(self.task2.destination_point, "Kiev")

    def test_put_list(self):
        self.auth(1)
        resp1 = self.api_client.get(
            self.details_url % (self.task1.pk,)
        )
        obj1 = self.deserialize(resp1).copy()
        obj2 = self.deserialize(resp1).copy()

        obj1['destination_point'] = "Gomel"
        obj2['destination_point'] = "Rio"
        obj2['resource_url'] = self.details_url % (self.task1.pk,)

        resp = self.api_client.patch(
            self.details_url % (self.task2.pk,),
            data={"objects": [obj1, obj2]}
        )

        self.assertHttpUnauthorized(resp)

        self.assertEqual(self.task2.destination_point, "Kiev")


    def test_delete_detail(self):
        self.auth(1)

        self.assertHttpUnauthorized(
            self.api_client.delete(
                self.details_url % (self.task2.pk,)
            )
        )

    def test_delete_list(self):
        self.auth(1)
        old_count = ByRwTask.objects.count()
        self.assertHttpAccepted(self.api_client.delete(self.list_url))
        new_count = ByRwTask.objects.count()

        self.assertEqual(old_count, new_count+1)

class TestByRwGatewayResource(ResourceTestCase):
    def setUp(self):
        super(TestByRwGatewayResource, self).setUp()

        self.super_user_email = u"supertest@test.ts"
        self.super_user_pass = u"test"

        self.user_email = u"test@test.ts"
        self.user_pass = u"test"

        self.url = u"/v1/byrwgateway/station/%s/"

        self.superuser = TrackTrainsUser.objects.create_superuser(
            self.super_user_email,
            self.super_user_pass)

        self.user = TrackTrainsUser.objects.\
            create_user(self.user_email, self.super_user_email, self.user_pass)

    def auth(self):
        auth_data = {
            'login': self.user_email,
            'password': self.user_pass
        }

        login_url = u'/v1/user/login/'

        self.api_client.post(
            login_url,
            data=auth_data
        )

    def test_station_unauthenticated(self):
        resp = self.api_client.get(
            self.url % 'A'
        )

        self.assertHttpUnauthorized(resp)

    def test_station_minsk(self):
        self.auth()

        resp = self.api_client.get(
            self.url % u'MINSK'
        )

        self.assertValidJSONResponse(resp)

        stations = self.deserialize(resp)

        self.assertEqual(stations[0]['name'], u'MINSK')

    def test_station_gomel(self):
        self.auth()

        resp = self.api_client.get(
            self.url % u'HOMIEĹ PASAŽYRSKI'
        )

        self.assertValidJSONResponse(resp)

        stations = self.deserialize(resp)

        self.assertEqual(stations[0]['name'], u'HOMIEĹ PASAŽYRSKI')

    def test_station_vitebsk(self):
        self.auth()

        resp = self.api_client.get(
            self.url % u'VICIEBSK PASAŽYRSKI'
        )

        self.assertValidJSONResponse(resp)

        stations = self.deserialize(resp)

        self.assertEqual(stations[0]['name'], u'VICIEBSK PASAŽYRSKI')

    def test_station_magilev(self):
        self.auth()

        resp = self.api_client.get(
            self.url % u'MAHILIOŬ 1'
        )

        self.assertValidJSONResponse(resp)

        stations = self.deserialize(resp)

        self.assertEqual(stations[0]['name'], u'MAHILIOŬ 1')

    def test_station_brest(self):
        self.auth()

        resp = self.api_client.get(
            self.url % u'BREST'
        )

        self.assertValidJSONResponse(resp)

        stations = self.deserialize(resp)

        self.assertEqual(stations[0]['name'], u'BREST')
