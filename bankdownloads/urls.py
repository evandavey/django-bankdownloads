from django.conf.urls import patterns, url, include
from django.views.generic import ListView
from bankdownloads.models import BankDownload

urlpatterns = patterns('',
    (r'^$', ListView.as_view(
        model=BankDownload,
    )),
)