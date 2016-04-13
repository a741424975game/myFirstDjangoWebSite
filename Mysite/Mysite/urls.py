from django.conf.urls import patterns, include, url
from django.contrib import admin
from Myapp.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Test.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',index),
    url(r'^index/$',index),
    # url(r'^user/$',user),
    url(r'^register/$',register),
    url(r'^login',login),
    url(r'^logout/$',logout),
    url(r'^animation/$',animation_index),
    url(r'^shared/animation/$',animation_shared),
    url(r'^shared/animation/host/(?P<name>\w+)/$',animation_shared_host),
    
)
