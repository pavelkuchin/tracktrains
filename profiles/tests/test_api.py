import re

from django.core import mail
from django.contrib.auth import authenticate

from tastypie.test import ResourceTestCase

from profiles.models import TrackTrainsUser


class TestTrackTrainsUserResource(ResourceTestCase):
    def setUp(self):
        super(TestTrackTrainsUserResource, self).setUp()

        self.super_user_email = u"supertest@test.ts"
        self.super_user_pass = u"test"

        self.user_email = u"test@test.ts"
        self.user_pass = u"test"

        self.userwi_email = u"testwi@test.ts"
        self.userwi_pass = u"test"

        self.list_url = u"/api/v1/user/"
        self.details_url = u"/api/v1/user/%d/"
        self.invite_url = u"/api/v1/user/invite/%s/"
        self.signup_url = u"/api/v1/user/signup/%s/"

        self.superuser = TrackTrainsUser.objects.create_superuser(
            self.super_user_email,
            self.super_user_pass)

        self.user = TrackTrainsUser.objects.\
            create_user(self.user_email, self.super_user_email, self.user_pass)

        self.user_without_invitation = TrackTrainsUser.objects.\
            create_user(self.userwi_email, self.super_user_email, self.userwi_pass)
        self.user_without_invitation.invites_counter=0
        self.user_without_invitation.save()

        self.post_data = {
            'email': 'newtest@test.ts',
            'inviter': self.details_url % (self.superuser.id),
            'invites_counter': 3,
            'password': 'test'
        }

    def auth(self, superuser=False):
        if superuser:
            auth_data = {
                'login': self.userwi_email,
                'password': self.userwi_pass
            }
        else:
            auth_data = {
                'login': self.user_email,
                'password': self.user_pass
            }

        login_url = u'/api/v1/user/login/'

        self.api_client.post(
            login_url,
            data=auth_data
        )

    def test_get_list_unauthorized(self):
        self.assertHttpUnauthorized(self.api_client.get(
            self.list_url,
            format='json'))

    def test_get_list_json(self):
        self.auth()
        resp = self.api_client.get(
            self.list_url,
            format='json'
        )
        self.assertValidJSONResponse(resp)

        self.assertEqual(len(self.deserialize(resp)['objects']), 3)

        self.assertEqual(self.deserialize(resp)['objects'][2], {
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
        self.auth()
        resp = self.api_client.get(
            self.details_url % (self.user.pk),
            format='json'
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
        self.auth()
        self.assertHttpMethodNotAllowed(
            self.api_client.post(
                self.list_url,
                format='json',
                data=self.post_data
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
        self.auth()
        orig_data = self.deserialize(
                        self.api_client.get(
                            self.details_url % (self.user.pk),
                            format='json'
                        )
                    )

        new_data = orig_data.copy()
        new_data['invites_counter'] = 100
        new_data['is_staff'] = True

        self.assertHttpMethodNotAllowed(
            self.api_client.put(
                self.details_url % (self.user.pk),
                format='json',
                data=new_data
            )
        )

    def test_delete_detail_unauthenticated(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.delete(
                self.details_url % (self.user.pk),
                format='json'
            )
        )

    def test_delete_detail(self):
        self.auth()
        self.assertHttpMethodNotAllowed(
            self.api_client.delete(
                self.details_url % (self.user.pk),
                format='json'
            )
        )

    def test_invite_signup(self):
        email = "unittest@test.ts"
        password = "testpassword"
        pattern = r"/signup/(.+)/"

        self.auth()

        # send invitation
        resp = self.deserialize(
            self.api_client.post(self.invite_url % (email))
        )

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], True, resp["message"])
        # checking email and finding token in email
        # The outbox attribute is created when the first message is sent.
        self.assertIsNotNone(mail.outbox)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]

        sres = re.search(pattern, msg.body)

        self.assertIsNotNone(sres)

        token = sres.group(1)

        self.assertIsNotNone(token)
        self.assertGreater(len(token), 0)

        # registartion with token
        resp = self.deserialize(
            self.api_client.post(
                self.signup_url % (token),
                format='json',
                data={'password': password}
            )
        )

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], True, resp["message"])

        user = authenticate(email=email, password=password)

        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.is_active, True)

    def test_bad_invitation(self):
        token = "bad token"
        password = "testpassword"

        # registartion with token
        resp = self.deserialize(
            self.api_client.post(
                self.signup_url % (token),
                format='json',
                data={'password': password}
            )
        )

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], False)

    def test_bad_password(self):
        email = "unittest@test.ts"
        password = ""
        pattern = r"/signup/(.+)/"

        self.auth()

        # send invitation
        resp = self.deserialize(
            self.api_client.post(self.invite_url % (email))
        )

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], True, resp["message"])
        # checking email and finding token in email
        # The outbox attribute is created when the first message is sent.
        self.assertIsNotNone(mail.outbox)
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]

        sres = re.search(pattern, msg.body)

        self.assertIsNotNone(sres)

        token = sres.group(1)

        self.assertIsNotNone(token)
        self.assertGreater(len(token), 0)

        # registartion with token
        resp = self.deserialize(
            self.api_client.post(
                self.signup_url % (token),
                format='json',
                data={'password': password}
            )
        )

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], False)

    def test_without_invitations(self):
        email = "unittest@test.ts"

        self.auth(True)

        # send invitation
        resp = self.deserialize(
            self.api_client.post(self.invite_url % (email))
        )

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], False)

    def test_login_success(self):
        auth_data = {
            'login': self.user_email,
            'password': self.user_pass
        }

        login_url = u'/api/v1/user/login/'

        resp = self.deserialize(self.api_client.post(
            login_url,
            data=auth_data
        ))

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], True)

    def test_login_wrong_params(self):
        auth_data = {
            'wrong': self.user_email,
            'again': self.user_pass
        }

        login_url = u'/api/v1/user/login/'

        resp = self.deserialize(self.api_client.post(
            login_url,
            data=auth_data
        ))

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], False)

    def test_login_wrong_password(self):
        auth_data = {
            'login': self.user_email,
            'password': "wrong password"
        }

        login_url = u'/api/v1/user/login/'

        resp = self.deserialize(self.api_client.post(
            login_url,
            data=auth_data
        ))

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], False)

    def test_login_account_disabled(self):
        auth_data = {
            'login': self.user_email,
            'password': self.user_pass
        }

        login_url = u'/api/v1/user/login/'

        self.user.is_active = False
        self.user.save()

        resp = self.deserialize(self.api_client.post(
            login_url,
            data=auth_data
        ))

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], False)

    def test_logout(self):
        auth_data = {
            'login': self.user_email,
            'password': self.user_pass
        }

        login_url = u'/api/v1/user/login/'
        logout_url = u'/api/v1/user/logout/'

        self.api_client.post(
            login_url,
            data=auth_data
        )

        # We can get details when logged in
        resp = self.api_client.get(
            self.details_url % (self.user.pk),
            format='json'
        )

        self.assertValidJSONResponse(resp)

        self.assertKeys(self.deserialize(resp),
            [u'email', u'inviter', u'invites_counter', \
            u'is_active', u'is_staff', u'resource_uri'])
        self.assertEqual(self.deserialize(resp)['email'], self.user_email)

        resp = self.deserialize(self.api_client.post(
            logout_url,
            data={}
        ))

        self.assertIsNotNone(resp)
        self.assertEqual(resp["success"], True)

        # We cannot get details when logged out
        self.assertHttpUnauthorized(
            self.api_client.get(self.details_url, format='json'))
