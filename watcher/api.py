from django.conf.urls import url
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import ReadOnlyAuthorization

from profiles.api import TrackTrainsUserResource
from utils.authorization import OwnerBasedAuthorization
from utils.gateways import GatewayByRw
from .models import ByRwTask


class ByRwTaskResource(ModelResource):
    owner = fields.ForeignKey(TrackTrainsUserResource, 'owner')

    class Meta:
        queryset = ByRwTask.objects.all()
        resource_name = 'byrwtask'
        authentication = SessionAuthentication()
        authorization = OwnerBasedAuthorization()


class ByRwGatewayResource(ModelResource):

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/station/(?P<name>.+)%s$" %
                    (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_station"),
                name="api_station"
            )
        ]

    def api_station(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)

        result = []

        name = kwargs.get('name')

        with GatewayByRw() as gw:
            result = gw.find_station(name)

        return self.create_response(request, result)

    class Meta:
        resource_name = 'byrwgateway'
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
