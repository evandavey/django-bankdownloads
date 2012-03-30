from django.db import models
import hashlib
import os
import csv
import re
import string
from datetime import *
import time
from traceback import print_exc
from django.db.models.signals import post_delete


from django.conf import settings
from django.core.files.storage import FileSystemStorage

from bankdownloads.utils.ofx import *

debug=False

creditHeaders=['credit',
               'credit($)',
               'transaction amount',
                'operation amount'
]

debitHeaders=['debit',
]

dateHeaders=['date',
            'operation date',
            'transaction date'
]


memoHeaders=['description',
]

payeeHeaders=['Counterparty account',
]




class OverwriteStorage(FileSystemStorage):
    
    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
    


class BankDownload(models.Model):


    class Meta:
        app_label = "bankdownloads"

    original_file_name=models.CharField(max_length=255,editable=False)
    original_file = models.FileField(upload_to='bankdownloads', storage=OverwriteStorage())
    upload_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    checksum = models.CharField(max_length=255,editable=False)
    records = models.IntegerField(blank=True,null=True)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    bank_id=models.CharField(max_length=255,editable=False)
    account_id=models.CharField(max_length=255,editable=False)
    mydata=[]
    
    def get_account_id(self):
        """
        Set account id from filename,expects <bankid>_<accountid>_<date>
        """
        
        ##load from file for rabobank
        reader=csv.reader(self.original_file)
        header=next(reader)
        
        if header[0]=="Account number :":
            return header[1]
        
        ##Otherwise get from filename
        f=self.original_file.name.split('/')[1]
        try:
            return f.split('-')[1]
        except:
            return None
     
    def get_bank_id(self):
        """
        Set bank id from filename,expects <bankid>_<accountid>_<date>
        """
        f=self.original_file.name.split('/')[1]
        try:
            return f.split('-')[0]
        except:
            return None       
            
	
    def save(self, *args, **kwargs):

        self.checksum=self.generate_checksum()
     
        super(BankDownload, self).save(*args, **kwargs) # Call the "real" save() method.
        
        self.original_file_name=os.path.basename(self.original_file.name)    
        self.data
        super(BankDownload, self).save(*args, **kwargs) # Call the "real" save() method.
            
            
        #else display some kind of warning???
    
   	

    def generate_checksum(self):
        md5 = hashlib.md5()
        self.original_file.open(mode='rb') 
        for chunk in iter(lambda: self.original_file.read(128*md5.block_size), ''): 
            md5.update(chunk)
        return md5.hexdigest()


    def containsDataForMonth(self,month):

        #TO DO
        #checks date range against month and returns Bool
            pass
            
    @property
    def data(self):
        self.mydata=[]
        extension = os.path.splitext(self.original_file.name)[1]

        if extension == ".ofx" or extension == ".qfx":
                self.load_ofx()
        else:
                self.load_csv()
                self.account_id=self.get_account_id()
                self.bank_id=self.get_bank_id()
              
        self.records=len(self.mydata)
        self.start_date=self.get_start_date(self.mydata)
        self.end_date=self.get_end_date(self.mydata)
        return self.mydata
        
    def load_csv(self):
        
        self.mydata=[]
        self.original_file.open()
        
        csvfile=self.original_file

        # Header search
        csvdata=[]
        prevline=[]
        headerFound=False
        for line in csvfile:
            line=next(csv.reader([line]))
            if len(prevline)==len(line) and not headerFound:
                headerFound=True
                csvdata.append(",".join(prevline))
                csvdata.append(",".join(line))
            elif headerFound:
                csvdata.append(",".join(line))
            else:
                prevline=line

        reader = csv.DictReader(csvdata)

     
        def filterPick(searchList,filter):
            for l in searchList:
                if filter(l):
                    return l
            
            return None
        
        creditRegex = re.compile('|'.join(creditHeaders),re.IGNORECASE).search
        memoRegex = re.compile('|'.join(memoHeaders),re.IGNORECASE).search
        debitRegex = re.compile('|'.join(debitHeaders),re.IGNORECASE).search
        dateRegex = re.compile('|'.join(dateHeaders),re.IGNORECASE).search
        payeeRegex = re.compile('|'.join(payeeHeaders),re.IGNORECASE).search

        creditCol = filterPick(reader.fieldnames,creditRegex)
        memoCol = filterPick(reader.fieldnames,memoRegex)
        debitCol = filterPick(reader.fieldnames,debitRegex)
        dateCol = filterPick(reader.fieldnames,dateRegex)
        payeeCol = filterPick(reader.fieldnames,payeeRegex)
        
        curr='AUD'
        fxcurr=curr
        fxrate=1.0
        
        try:
            for row in reader:
          
                
                dt=row[dateCol]
                dt=dt.translate(None,"-/\\")
                
                try:
                    dt=datetime.strptime(dt,'%d%m%Y').date()
                except:
                    raise Exception('Error: Could not parse date')
                    dt=None
                    
                try:
                    credit=row[creditCol]
                    credit=credit.translate(None,",$")
                    credit=float(credit)
                except:
                    if debug:
                        print 'Warning: Could not parse credit'
                    credit=None
                           
                try:
                    debit=row[debitCol]
                    debit=debit.translate(None,",$")
                    debit=abs(float(debit))
                except:
                    if debug:
                        print 'Warning: Could not parse debit'
                    debit=None   
                    
                try:
                    memo=row[memoCol]
                except:
                    if debug:
                        print 'Warning: Could not parse memo'
                    memo=None 
                    
                try:
                    payee=row[payeeCol]
                except:
                    if debug:
                        print 'Warning: Could not parse payee'
                    payee=None
                
                if credit:
                    val=credit
                elif debit:
                    val=debit*-1
                else:
                    raise Exception('Error: No debit or credit data found')
                    val=None           
            
                fxamount=val
                
                # use of time() should keep transid unique
                hashstr="%s%s%s%s%s%s" % (self.checksum,dt,val,payee,memo,time.time())
                transid=hashlib.md5(hashstr).hexdigest()
                
               
                d={"transid":transid,
                   "bankid":self.get_bank_id(),
                   "accountid":self.get_account_id(),
                   "date":dt,
                   "payee":payee,
                   "memo":memo,
                   "value":val,
                   "currency":curr,
                   "fxcurrency":fxcurr,
                   "fxamount":fxamount,
                   "fxrate":fxrate,
                }
                
                self.mydata.append(d)
        
        except csv.Error, e:
                print('file %s, line %d: %s' % (filename, reader.line_num, e))
     
        
    def load_ofx(self):

        self.mydata=[]
        self.original_file.open()
        ofx = OfxParser.parse(self.original_file.file)
        self.original_file.seek(0)
        try:
            for t in ofx.bank_account.statement.transactions:
                val=float(t.amount)
                payee=cleanStr(t.payee)
                memo=cleanStr(t.memo)
                dt=parseDate(cleanStr(t.date))
                accid=cleanStr(ofx.bank_account.number)
                bankid=cleanStr(ofx.bank_account.routing_number)
                transid=cleanStr(t.id)
                desc=payee + "-" + memo

                self.account_id=accid
                self.bank_id=bankid
          

                curr=cleanStr(ofx.bank_account.currency)


                #defaults to be overridden in subclass
                fxrate=1
                fxcurr=curr
                fxamount=val

                # use of time() should keep transid unique
                hashstr="%s%s%s%s%s%s" % (transid,dt,val,payee,memo,time.time())
                transid=hashlib.md5(hashstr).hexdigest()


                d={"transid":transid,
                   "bankid":bankid,
                   "accountid":accid,
                   "date":dt,
                   "payee":payee,
                   "memo":memo,
                   "value":val,
                   "currency":curr,
                   "fxcurrency":fxcurr,
                   "fxamount":fxamount,
                   "fxrate":fxrate,
                }

                self.mydata.append(d)

            return
        except:
            print_exc()
            raise Exception('Error: Could not read ofx %s' % self.original_filename)

    def get_end_date(self,data):

        end_date=None
        for row in data:
            dt=row["date"]

            if end_date is None or dt>=end_date:
                end_date=dt
                
        return end_date

    def get_start_date(self,data):

        start_date=None
        for row in data:
            dt=row["date"]

            if start_date is None or dt<=start_date :
                start_date=dt  
                
        return start_date
        
    def export_ofx(self):
        
        import StringIO
        data=self.data
        
        if data:
            ofx = StringIO.StringIO()
            ofxexport(ofx,data)
            ofxstring=ofx.getvalue()
            ofx.close()

            return ofxstring
            
        return ""
 
def delete_filefield(sender, **kwargs):
    """Automatically deleted files when records removed.
    """
    model = kwargs.get('instance')
    model.original_file.delete(save=False)

post_delete.connect(delete_filefield, BankDownload)

             
def cleanStr(str):

    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    str=''.join(c for c in str if c in valid_chars)

    return str



def parseDate(dt):

    dt=dt.strip()

    if len(dt) == 14:
      dt = datetime.strptime(dt, "%Y%m%d000000")
    else:
      dt = datetime.strptime(dt, "%Y%m%d")
      
    dt=dt.date()

    return dt		