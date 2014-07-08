from django.conf.urls import url
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.utils import trailing_slash
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication

from .models import TrackTrainsUser


class TrackTrainsUserResource(ModelResource):
    class Meta:
        queryset = TrackTrainsUser.objects.all()
        resource_name = 'user'
        authentication = BasicAuthentication()
        authorization = ReadOnlyAuthorization()
        filtering = {'email': ALL}
        fields = ['email', 'inviter', 'invites_counter', 'is_active', 'is_staff']

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/signup%s$" % (self._meta.resource_name, trailing_slash()), 
                self.wrap_view("signup"), 
                name="api_signup"),
            url(r"(?P<resource_name>%s)/invite%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("invite"),
                name="api_invite")
        ]

    def signup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # TODO sugnup implementation

        result = {'result': 'stub for signup'}

        self.log_throttled_access(request)
        return self.create_response(request, result)

    def invite(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # TODO invite implementation

        result = {'result': 'stub for invite'}

        self.log_throttled_access(request)
        return self.create_response(request, result)
