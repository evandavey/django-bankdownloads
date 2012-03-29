#django-bankdownloads

* django app to handle bank transaction downloads

* imports ofx (open financial exchange format) via the ofxparse library

* imports csv using regex to match data columns

* bankid and accountid taken from original file if possible, otherwise from a filename in the format

	<bankid>-<accountid>-YYYYMMDD.<ext>
		
* creates a standardised data dictionary with headers:

	date
	transid
	value
	currency
	memo
	payee
	accountid
	bankid
	fxcurrency
	fxrate
	fxamount
	

##Install

1. Get the code

	> git clone git://github.com/evandavey/django-bankdownloads.git django-bankdownloads
	
2. Install via pip

	> pip install django-bankdownloads
	
3. Add 'bankdownloads' to INSTALLED_APPS

##Use

* provides a 'BankDownload' class that can be reused in other applications

	> mydownload = BankDownload()
	> mydownload.original_file=<file>
	> mydownload.save()
	
* access standardised data via the 'data' property

	> data = mydownload.data
	


