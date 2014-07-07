from django.conf.urls import patterns, include, url
from django.contrib import admin

from tastypie.api import Api

from profiles.api import TrackTrainsUserResource

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(TrackTrainsUserResource())

urlpatterns = patterns('',
    url('^api/', include(v1_api.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
