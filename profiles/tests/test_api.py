from tastypie.test import ResourceTestCase

from profiles.models import TrackTrainsUser


class TrackTrainsUserResource(ResourceTestCase):
    def setUp(self):
        super(TrackTrainsUserResource, self).setUp()

        self.super_user_email = "supertest@test.ts"
        self.super_user_pass = "test"

        self.user_email = "test@test.ts"
        self.user_pass = "test"

        self.default_url = "/api/v1/users/"

        TrackTrainsUser.objects.create_superuser(
            self.super_user_email,
            self.super_user_pass)

        TrackTrainsUser.objects.\
            create_user(self.user_email, self.super_user_email, self,user_pass)
