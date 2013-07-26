from django.conf.urls import patterns, url

from bolt import views

urlpatterns = patterns('',
    url(r'^$', views.input, name='index'),
    url(r'^input/*$', views.input, name='input'),
    url(r'^better-choice/*$', views.better_choice, name='better-choice'),
    url(r'^retype/*$', views.retype_ref, name='retype-ref'),
    url(r'^translation/*$', views.translation, name='translation'),
)
