from django.conf import settings
from django.conf.urls import patterns, include, url

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', "logs.views.group_list", name="group_list"),
    url(r'^group/(?P<group_id>\d+)/', "logs.views.group_details", name="group_details"),
    url(r'^group/star/(?P<group_id>\d+)/', "logs.views.group_star", name="group_star"),
    url(r'^group/resolve/(?P<group_id>\d+)/', "logs.views.group_resolve", name="group_resolve"),
    url(r'^group/remove/(?P<group_id>\d+)/', "logs.views.group_remove", name="group_remove"),

    url(r'^favorites/$', "logs.views.favorites_list", name="favorites_list"),

    url(r'^list/', "logs.views.log_list", name="log_list"),
    url(r'^log/(?P<log_id>\d+)/', "logs.views.log_details", name="log_details"),

    # url(r'^sloggy/', include('sloggy.foo.urls')),

    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^css/(.*)$', 'django.views.static.serve',
         { 'document_root': settings.MEDIA_ROOT + "/css", 'show_indexes': True }),
        (r'^images/(.*)$', 'django.views.static.serve',
         { 'document_root': settings.MEDIA_ROOT + "/images", 'show_indexes': True }),
        (r'^js/(.*)$', 'django.views.static.serve',
         { 'document_root': settings.MEDIA_ROOT + "/js", 'show_indexes': True })
    )
