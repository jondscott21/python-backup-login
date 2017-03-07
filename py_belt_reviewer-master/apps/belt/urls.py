from django.conf.urls import url, include
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^process$', views.process),
    url(r'^books$', views.books),
    url(r'^log_in$', views.log_in),
    url(r'^log_out$', views.log_out),
    url(r'^books/(?P<id>\d+)$', views.book_id),
    url(r'^user/(?P<id>\d+)$', views.user),
    url(r'^add$', views.add),
    url(r'^proc_book$', views.proc_book),
    url(r'^proc_review/(?P<id>\d+)$', views.proc_review),
    url(r'^.*$', views.error),

]
