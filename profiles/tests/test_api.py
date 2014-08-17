from tastypie.test import ResourceTestCase

from profiles.models import TrackTrainsUser


class TrackTrainsUserResource(ResourceTestCase):
    def setUp(self):
        super(TrackTrainsUserResource, self).setUp()

        self.super_user_email = u"supertest@test.ts"
        self.super_user_pass = u"test"

        self.user_email = u"test@test.ts"
        self.user_pass = u"test"

        self.list_url = u"/api/v1/user/"
        self.details_url = u"/api/v1/user/%d/"

        self.superuser = TrackTrainsUser.objects.create_superuser(
            self.super_user_email,
            self.super_user_pass)

        self.user = TrackTrainsUser.objects.\
            create_user(self.user_email, self.super_user_email, self.user_pass)

        self.post_data = {
            'email': 'newtest@test.ts',
            'inviter': self.details_url % (self.superuser.id),
            'invites_counter': 3,
            'password': 'test'
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
        self.assertHttpUnauthorized(self.api_client.get(
            self.list_url,
            format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(
            self.list_url,
            format='json',
            authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 2)

        self.assertEqual(self.deserialize(resp)['objects'][1], {
            u'resource_uri': self.details_url % (self.user.pk),
            u'email': self.user_email,
            u'inviter': self.details_url % (self.superuser.pk),
            u'invites_counter': 3,
            u'is_active': True,
            u'is_staff': False
        })

    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(
            self.api_client.get(self.details_url, format='json'))

    def test_get_detail_json(self):
        resp = self.api_client.get(
            self.details_url % (self.user.pk),
            format='json',
            authentication=self.get_credentials()
        )

        self.assertValidJSONResponse(resp)

        self.assertKeys(self.deserialize(resp),
            [u'email', u'inviter', u'invites_counter', \
            u'is_active', u'is_staff', u'resource_uri'])
        self.assertEqual(self.deserialize(resp)['email'], self.user_email)


    def test_post_list_unauthenticated(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.post(
                self.list_url,
                format='json',
                data=self.post_data
            )
        )

    def test_post_list(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.post(
                self.list_url,
                format='json',
                data=self.post_data,
                authentication=self.get_credentials()
            )
        )

    def test_put_details_unauthenticated(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.put(
                self.details_url % (self.user.pk),
                format='json',
                data={}
            )
        )

    def test_put_details(self):
        orig_data = self.deserialize(
                        self.api_client.get(
                            self.details_url % (self.user.pk),
                            format='json',
                            authentication=self.get_credentials()
                        )
                    )

        new_data = orig_data.copy()
        new_data['invites_counter'] = 100
        new_data['is_staff'] = True

        self.assertHttpMethodNotAllowed(
            self.api_client.put(
                self.details_url % (self.user.pk),
                format='json',
                data=new_data,
                authentication=self.get_credentials()
            )
        )

    def test_delete_detail_unauthenticated(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.delete(self.details_url % (self.user.pk), format='json')
        )

    def test_delete_detail(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.delete(
                self.details_url % (self.user.pk),
                format='json',
                authentication=self.get_credentials()
            )
        )
