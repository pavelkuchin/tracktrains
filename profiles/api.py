from tastypie.resources import ModelResource

from .models import TrackTrainsUser


class TrackTrainsUserResource(ModelResource):
    class Meta:
        queryset = TrackTrainsUser.objects.all()
        resource_name = 'user'
