from django.test import TestCase
from django.contrib.auth import authenticate

from profiles.models import TrackTrainsUser


class TrackTrainsUserTest(TestCase):
    def setUp(self):
        # the self.superuser variable is object but for create_user it will be
        # convert to email string due to __unicode__ method.
        self.superuser = TrackTrainsUser.objects.\
                          create_superuser("supertest@test.ts", "test")

    def test_create(self):
        email = "user@test.ts"

        TrackTrainsUser.objects.\
          create_user(email, self.superuser, "test")

        user = TrackTrainsUser.objects.get(email=email)

        self.assertEqual(user.invites_counter, 3)
        self.assertEqual(user.inviter.id, self.superuser.id)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_auth(self):
        email = "user@test.ts"
        password = "test"

        TrackTrainsUser.objects.\
          create_user(email, self.superuser, password)

        user = authenticate(email=email, password=password)

        self.assertIsNotNone(user)

        user = authenticate(email=email, password="wrongpassword")

        self.assertIsNone(user)

    def test_change_pass(self):
        email = "user@test.ts"
        password = "test"
        new_password = "newpassword"

        TrackTrainsUser.objects.\
            create_user(email, self.superuser, password)

        user = authenticate(email=email, password=password)

        self.assertIsNotNone(user)

        user.set_password(new_password)
        user.save()

        user = authenticate(email=email, password=new_password)

        self.assertIsNotNone(user)

    def test_exceed_invitations_limit(self):
        inviter = TrackTrainsUser.objects.\
            create_user("inviter@test.ts", self.superuser, "test")
        inviter.invites_counter = 2
        inviter.save()

        TrackTrainsUser.objects.\
            create_user("user1@test.ts", inviter, "test")

        TrackTrainsUser.objects.\
            create_user("user2@test.ts", inviter, "test")

        with self.assertRaises(ValueError):
            TrackTrainsUser.objects.\
                create_user("user3@test.ts", inviter, "test")

    def test_user_already_exists(self):
        TrackTrainsUser.objects.\
            create_user("test@test.ts", self.superuser, "test")

        with self.assertRaises(ValueError):
            TrackTrainsUser.objects.\
                create_user("test@test.ts", self.superuser, "new_test")

    def test_validation_email(self):
        # empty email
        with self.assertRaises(ValueError):
            TrackTrainsUser.objects.\
                create_user("", self.superuser, "test")

        # TODO move to forms validation
        # invalid email
        #with self.assertRaises(ValueError):
        #    TrackTrainsUser.objects.\
        #        create_user("test@test", self.superuser, "test")

        #with self.assertRaises(ValueError):
        #    TrackTrainsUser.objects.\
        #        create_user("@", self.superuser, "test")

        #with self.assertRaises(ValueError):
        #    TrackTrainsUser.objects.\
        #        create_user("test", self.superuser, "test")

    def test_wrong_inviter(self):
        with self.assertRaises(ValueError):
            TrackTrainsUser.objects.\
                create_user("test@test.ts", "wrong_inviter@test.ts", "test")

        with self.assertRaises(ValueError):
            TrackTrainsUser.objects.\
                create_user("test@test.ts", "", "test")

    def test_short_name(self):
        email = "test@test.ts"
        user = TrackTrainsUser.objects.\
                create_user(email, self.superuser, "test")
        self.assertEqual(user.get_short_name(), email)
