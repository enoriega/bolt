from django.conf.urls import patterns, url

from bolt import views

urlpatterns = patterns('',
    url(r'^$', views.input, name='index'),
    url(r'^input/*$', views.input, name='input'),
    url(r'^better-choice/*$', views.better_choice, name='better-choice'),
    url(r'^selected/*$', views.selected, name='selected'),
    url(r'^retype/*$', views.retype_ref, name='retype-ref'),
    url(r'^translation/*$', views.translation, name='translation'),
    url(r'^read_sausage/(\d+)/$', views.read_sausage, name='read-sausage'),
    url(r'^logistic_classifiation/$', views.logistic_classification, name='logistic-classification'),
    url(r'^linear_regression/$', views.linear_regression, name='linear-regression'),
)
