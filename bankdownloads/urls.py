from django.conf.urls import patterns, url, include
from django.views.generic import ListView
from bankdownloads.models import BankDownload
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = patterns('',
    (r'^$', login_required(ListView.as_view(
        model=BankDownload,
    ))),
)