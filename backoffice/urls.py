# coding=utf-8
from django.conf.urls import  url
from backoffice.views import *

urlpatterns = [
    url(r'^backoffice/getPublishedDate/$', getPublishedDate, name='getPublishedDate'),
]