from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import SessionAuthentication

from profiles.api import TrackTrainsUserResource
from utils.authorization import OwnerBasedAuthorization
from .models import ByRwTask


class ByRwTaskResource(ModelResource):
    owner = fields.ForeignKey(TrackTrainsUserResource, 'owner')

    class Meta:
        queryset = ByRwTask.objects.all()
        resource_name = 'byrwtask'
        authentication = SessionAuthentication()
        authorization = OwnerBasedAuthorization()
