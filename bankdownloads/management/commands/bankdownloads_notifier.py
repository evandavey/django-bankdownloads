from django.core.management.base import BaseCommand, CommandError
from datetime import *
from django.core.mail import send_mail
from django.conf import settings


from bankdownloads.models import BankDownload

class Command(BaseCommand):
    help = 'Sends bankdownload warning emails'

    def handle(self, *args, **options):
       
        excludes_list = getattr(settings, 'BANKDOWNLOADS_NOTIFIER_EXCLUDES', ['-'])
        toemails = getattr(settings, 'BANKDOWNLOADS_EMAILS', None)
        
        excludes={}
        for e in excludes_list:
            excludes[e]=1
        
        #get unique banks
        banks=BankDownload.objects.values_list('bank_id').distinct()
        
        today = datetime.today()
        
        warning_date = (today.replace(day=1) - timedelta(days=15)).date()
        print "Warning date is %s" % warning_date
        
        last_dates=[]
        missing_found=False
        for b in banks:
            
            #get unique accounts
            accounts=BankDownload.objects.filter(bank_id=b[0]).values_list('account_id').distinct()
            for a in accounts:
                try:
                    
                    excludes[b[0].strip()+"-"+a[0].strip()]
                except:
                    #find last data date
                    last_date=BankDownload.objects.filter(bank_id=b[0],account_id=a[0]).order_by('-end_date')[0]
                    if last_date.end_date is None or last_date.end_date<warning_date:
                        missing_found=True
                        last_dates.append('**MISSING** %s - %s: %s'%(b[0].strip(),a[0].strip(),last_date.end_date))
                    else:
                        last_dates.append('%s - %s: %s'%(b[0].strip(),a[0].strip(),last_date.end_date))
                    
        
        subj="BANK DOWNLOADS"
        msg=""
        msg+=("Data has been downloaded as at:\n\n")   
        for d in last_dates:
            msg+=("\t%s\n" % (d))
        
        #print msg  
        if toemails and missing_found:
            print 'Sending email'
            send_mail(subj, msg, settings.EMAIL_HOST_USER,toemails, fail_silently=False)
        
  