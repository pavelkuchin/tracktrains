import time
import datetime

from django.conf.urls import url
from django.http import HttpResponseBadRequest
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import ReadOnlyAuthorization

from profiles.api import TrackTrainsUserResource
from utils.gateways import GatewayByRw
from .models import ByRwTask
from .authorization import TaskAuthorization


class ByRwTaskResource(ModelResource):
    owner = fields.ForeignKey(TrackTrainsUserResource, 'owner')

    class Meta:
        queryset = ByRwTask.objects.all()
        resource_name = 'byrwtask'
        authentication = SessionAuthentication()
        authorization = TaskAuthorization()


class ByRwGatewayResource(ModelResource):

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/station/(?P<name>.+)%s$" %
                    (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_station"),
                name="api_station"
            ),
            url(r"^(?P<resource_name>%s)/train%s$" %
                    (self._meta.resource_name, trailing_slash()),
                self.wrap_view("api_train"),
                name="api_train"
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

    def api_train(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)

        result = []

        date = request.GET.get('date')
        departure = request.GET.get('departure_point')
        destination = request.GET.get('destination_point')
        query = request.GET.get('query')

        if not (date and departure and destination and query):
            return HttpResponseBadRequest(
                "Request expects date,"
                "departure_point,"
                "destination_point and query parameters"
            )

        time_struct = time.strptime(date.split('T')[0], "%Y-%m-%d")
        typed_date = datetime.datetime(*time_struct[:6])

        with GatewayByRw() as gw:
            result = gw.find_train(typed_date, departure, destination, query)

        return self.create_response(request, result)

    class Meta:
        resource_name = 'byrwgateway'
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
