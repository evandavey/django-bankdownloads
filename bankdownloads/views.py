import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django_tables2 import RequestConfig

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext

from bankdownloads.models import BankDownload

class BankDownloadTable(tables.Table):
    
    class Meta:
        model = BankDownload
        exclude = ['id','original_file','checksum','bank_id','account_id']
        

@login_required(login_url='/accounts/login')   
def index(request):

    table = BankDownloadTable(BankDownload.objects.all())
    RequestConfig(request).configure(table)

    ct={'table':table,
    }

    return render_to_response('bankdownloads/bankdownload_list.html',ct,context_instance=RequestContext(request))