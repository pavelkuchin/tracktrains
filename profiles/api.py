import logging

from django.conf.urls import url
from django.core import signing
from django.core.mail import send_mail
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.utils import trailing_slash
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication

from .models import TrackTrainsUser
from utils import email

log = logging.getLogger(__name__)

class TrackTrainsUserResource(ModelResource):
    inviter = fields.ForeignKey('self', 'inviter', null=True, blank=True)

    class Meta:
        queryset = TrackTrainsUser.objects.all()
        resource_name = 'user'
        authentication = BasicAuthentication()
        authorization = ReadOnlyAuthorization()
        filtering = {'email': ALL}
        allowed_methods = ['get']
        fields = ['email', 'inviter', 'invites_counter', 'is_active', 'is_staff']

    def prepend_urls(self):
        return [
            url(r"(?P<resource_name>%s)/signup/(?P<hash>.+)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("signup"),
                name="api_signup"),
            url(r"(?P<resource_name>%s)/invite/(?P<email>.+)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("invite"),
                name="api_invite")
        ]

    def signup(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.throttle_check(request)

        inv_hash = kwargs['hash']

        try:
            invitation = signing.loads(inv_hash, salt='profile')

            password = request.POST.get('password')

            if len(password):
                TrackTrainsUser.objects.create_user(invitation['to'], invitation['from'], password)

                log.debug(invitation)
                log.info('Invitation has been accepted by %s' % invitation['to'])
                result = {'success': True}
            else:
                # TODO complex password check out
                msg = 'Empty string is not a valid password.'
                log.warning(msg)
                result = {'success': False, 'msg': msg}
        except:
            # TODO advanced exceptions processing.
            #       Here can be various exceptions
            msg = 'Bad invitation'
            log.exception(msg)
            result = {'success': False, 'msg': msg}

        self.log_throttled_access(request)
        return self.create_response(request, result)

    def invite(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)


        if request.user.invites_counter > 0:
            invitation = {
                'from': request.user.email,
                'to': kwargs['email']
            }
            log.debug(invitation)

            signed_invitation = signing.dumps(invitation, salt='profile')

            email.send_invitation_email(request, invitation['from'], invitation['to'], signed_invitation)

            result = {'success': True}
        else:
            result = {'success': False, 'message': "User can't send more invitations. Limit has came."}

        self.log_throttled_access(request)
        return self.create_response(request, result)
