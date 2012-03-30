from django.contrib import admin
from bankdownloads.models import *


class BankDownloadAdmin(admin.ModelAdmin):
	""" Object to control the behaviour of the linked object in the Admin interface
	"""
	list_display = ['original_file_name','checksum','upload_date','records','start_date','end_date']
	list_filter = ['bank_id','account_id']
	ordering = ['upload_date']
	search_fields = ['original_file']



admin.site.register(BankDownload,BankDownloadAdmin)	








	
