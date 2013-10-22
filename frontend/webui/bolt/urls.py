from django.conf.urls import patterns, url

from bolt import views, ok_index, error_index, m4_index, l4_index, index

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    #url(r'^$', views.input, {'index': index, 'name':'input'}, name='index'),
    url(r'^input/*$', views.input, {'index': index, 'name':'input'}, name='input'),
    url(r'^test/*$', views.test, {'index': index, 'name':'test'}, name='test'),
    url(r'^l4/*$', views.input, {'index': l4_index, 'name':'l4'}, name='l4'),
    url(r'^m4/*$', views.input, {'index': m4_index, 'name':'m4'}, name='m4'),
    url(r'^better-choice/*$', views.better_choice, name='better-choice'),
    url(r'^selected/*$', views.selected, name='selected'),
    url(r'^retype/*$', views.retype_ref, name='retype-ref'),
    url(r'^translation/*$', views.translation, name='translation'),
    url(r'^read_sausage/(\d+)/$', views.read_sausage, name='read-sausage'),
    url(r'^logistic_classifiation/$', views.logistic_classification, name='logistic-classification'),
    url(r'^linear_regression/$', views.linear_regression, name='linear-regression'),
    url(r'^exit/$', views.exit, name='exit'),
)
