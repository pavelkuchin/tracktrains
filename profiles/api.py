import logging
import json

from django.conf.urls import url
from django.core import signing
from django.contrib.auth import authenticate, login, logout
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.utils import trailing_slash
from tastypie.authentication import SessionAuthentication
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpForbidden, HttpBadRequest

from .models import TrackTrainsUser
from .authorization import UserAuthorization
from utils import email


log = logging.getLogger(__name__)


class TrackTrainsUserResource(ModelResource):
    inviter = fields.ForeignKey('self', 'inviter', null=True, blank=True)

    class Meta:
        queryset = TrackTrainsUser.objects.all()
        resource_name = 'user'
        authentication = SessionAuthentication()
        authorization = UserAuthorization()
        filtering = {'email': ALL}
        allowed_methods = ['get', 'delete']
        fields = ['id', 'email', 'inviter', 'invites_counter', 'is_active', \
                  'is_staff', 'tasks_limit']

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/signup/(?P<hash>.+)%s$"
                    % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_signup"),
                name="api_signup"),
            url(r"(?P<resource_name>%s)/invite/(?P<email>.+)%s$"
                    % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_invite"),
                name="api_invite"),
            url(r"(?P<resource_name>%s)/login%s$"
                    % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_login"),
                name="api_login"),
            url(r"(?P<resource_name>%s)/logout%s$"
                    % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_logout"),
                name="api_logout"),
            url(r"(?P<resource_name>%s)/session%s$"
                    % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_session"),
                name="api_session"),
            url(r"(?P<resource_name>%s)/change_password%s$"
                    % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_change_password"),
                name="api_change_password")
        ]

    def api_change_password(self, request, **kwargs):
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)

        body = json.loads(request.body)

        if body and 'password' in body and 'new_password' in body:
            if request.user.check_password(body['password']):
                request.user.set_password(body['new_password'])
                request.user.save()
            else:
                msg = "The password is incorrect."
                log.warning(msg)
                raise ImmediateHttpResponse(HttpBadRequest(msg))
        else:
            msg = "The current password and a new password are required"
            log.warning(msg)
            raise ImmediateHttpResponse(HttpBadRequest(msg))

        result = {'success': True, 'message':'Your password has been changed.'}

        return self.create_response(request, result)

    def api_login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
#        self.throttle_check(request)

        result = {}
        body = json.loads(request.body)

        if body and 'password' in body and 'login' in body:
            email = body['login']
            password = body['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    msg = "You are logged in"
                    result = {'success': True, 'message': msg}
                else:
                    msg = "User account is disabled"
                    log.warning(msg)
                    raise ImmediateHttpResponse(HttpForbidden(msg))
            else:
                msg = "Invalid login or password"
                log.warning(msg)
                raise ImmediateHttpResponse(HttpBadRequest(msg))
        else:
            msg = "User login and password are required"
            log.warning(msg)
            raise ImmediateHttpResponse(HttpBadRequest(msg))

#        self.log_throttled_access(request)
        return self.create_response(request, result)

    def api_logout(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
#        self.throttle_check(request)

        msg = "You are logged out"
        result = {'success': True, 'message': msg}
        logout(request)

#        self.log_throttled_access(request)
        return self.create_response(request, result)

    def api_signup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
#        self.throttle_check(request)

        inv_hash = kwargs['hash']

        try:
            invitation = signing.loads(inv_hash, salt='profile')

            log.debug("Request Body: %s" % request.body)

            body = json.loads(request.body)

            if body and body['password']:
                password = body['password']
                TrackTrainsUser.objects.create_user(invitation['to'],
                    invitation['from'], password)

                log.debug(invitation)
                log.info('Invitation has been accepted by %s'
                            % invitation['to'])
                result = {'success': True,
                          'message': 'User has been registered'}
            else:
                # TODO complex password check out
                msg = 'Empty string is not a valid password.'
                log.warning(msg)
                raise ImmediateHttpResponse(HttpBadRequest(msg))
        except:
            # TODO advanced exceptions processing.
            #       Here can be various exceptions
            msg = 'Bad invitation'
            log.exception(msg)
            raise ImmediateHttpResponse(HttpBadRequest(msg))

#        self.log_throttled_access(request)
        return self.create_response(request, result)

    def api_invite(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
#        self.throttle_check(request)

        if request.user.invites_counter > 0:
            invitation = {
                'from': request.user.email,
                'to': kwargs['email']
            }
            log.debug(invitation)

            signed_invitation = signing.dumps(invitation, salt='profile')

            email.send_invitation_email(invitation['from'], invitation['to'],
                signed_invitation)

            result = {'success': True, 'message': 'User has been invited'}
        else:
            msg = "User can't send more invitations. Limit has came."
            raise ImmediateHttpResponse(HttpForbidden(msg))

#        self.log_throttled_access(request)
        return self.create_response(request, result)

    def api_session(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
#        self.throttle_check(request)

        bundle = self.build_bundle(obj=request.user, request=request)
        bundle = self.full_dehydrate(bundle)

#        self.log_throttled_access(request)
        return self.create_response(request, bundle)
