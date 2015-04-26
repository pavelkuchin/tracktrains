from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from profiles.api import TrackTrainsUserResource
from watcher.api import ByRwTaskResource, ByRwGatewayResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(TrackTrainsUserResource())
v1_api.register(ByRwTaskResource())
v1_api.register(ByRwGatewayResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(v1_api.urls))
)
