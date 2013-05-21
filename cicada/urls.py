#coding:utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# admin.autodiscover()
# from admin import *
# from views import *
# from cicada.admin.views import *
# from cicada.admin import views
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cicada.views.home', name='home'),
    # url(r'^cicada/', include('cicada.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.urls)),
    url(r'^$',views.index),
    url(r'^topic_suggest/$',views.topic_suggest),
    url(r'^question_save/$',views.question_save),
    
)
#后台管理
urlpatterns += patterns(
	'cicada.admin.views',
	url(r'^admin/$','index'),
    url(r'^admin/edit$','edit'),
)
