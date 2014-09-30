from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from profiles.api import TrackTrainsUserResource
from .models import ByRwTask


class ByRwTaskResource(ModelResource):
    owner = fields.ForeignKey(TrackTrainsUserResource, 'owner')

    class Meta:
        queryset = ByRwTask.objects.all()
        resource_name = 'task'
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
