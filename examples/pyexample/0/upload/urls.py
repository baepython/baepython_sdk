from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',
    url(r'^$', 'upload.views.index'),
    url(r'^upload$', 'upload.views.upload'),
)

