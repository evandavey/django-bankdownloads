import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext

from bankdownloads.models import BankDownload

class BankDownloadTable(tables.Table):
    
    
    name = tables.LinkColumn('bankdownload_detail', args=[A('pk')])
    
    
    class Meta:
        model = BankDownload
        exclude = []
        

@login_required(login_url='/accounts/login')   
def index(request):

    table = BankDownloadTable(BankDownload.objects.all())
    table.paginate(page=request.GET.get("page", 1))
    table.order_by = request.GET.get("sort")

    ct={'table':table,
    }

    return render_to_response('bankdownloads/bankdownload_list.html',ct,context_instance=RequestContext(request))