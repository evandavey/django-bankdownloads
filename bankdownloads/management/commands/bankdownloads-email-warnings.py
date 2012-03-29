from django.core.management.base import BaseCommand, CommandError

from datetime import datetime

class Command(BaseCommand):
    args = '<start_date YYYYMMDD> <end_date YYYYMMDD>'
    help = 'Sends bankdownload warning emails'

def handle(self, *args, **options):

    self.stdout.write('Not implemented\n')
    # if len(args) < 2:
	   #       raise CommandError('Requires arguments %s' % self.args)
	   #   
	   # 
	   #   try:
	   #       startdate=datetime.strptime(args[0],'%Y%m%d')
	   #       enddate=datetime.strptime(args[1],'%Y%m%d')
	   #   except:
	   #       raise CommandError('Date format must be YYYYMMDD')  
	   #   
	   #   self.stdout.write('Fetching prices between %s and %s\n' % (startdate,enddate))
	   #   
	   #   fetch_investment_prices(startdate,enddate)
	   #   fetch_currency_prices(startdate,enddate)
	   #   
	