#django-bankdownloads

* django app to import and standardise bank transaction downloads

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
	
* outputs data in ofx format
	

##Requirements

* working django site

##Install

1. Get the code

	> git clone git://github.com/evandavey/django-bankdownloads.git django-bankdownloads
	
2. Install via pip

	> pip install django-bankdownloads
	
3. Add 'bankdownloads' to INSTALLED_APPS

4. Add BANKDOWNLOADS_IMPORT_PATH,BANKDOWNLOADS_OUTPUT_PATH,BANKDOWNLOADS_EMAILS and BANKDOWNLOADS_NOTIFIER_EXCLUDES to settings

##Use

* provides a 'BankDownload' class that can be reused in other applications

	> mydownload = BankDownload()
	
	> mydownload.original_file=[file]
	
	> mydownload.save()
	
* access standardised data via the 'data' property

	> data = mydownload.data
	
	> ofx = mydownload.export_ofx()
	
* use management command bankdownloads_notifier to email if data is missing for a given month

* use management command bankdownloads_processor to batch import bank downloads and output standardised ofx

##Authors

Evan Davey evan.davey@cochranedavey.com

##Licenses

CC-SA-NC

[Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License][cc-nc-sa].

![][img-cc-nc-sa]


[cc-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/3.0/

[img-cc-nc-sa]: http://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png


	


