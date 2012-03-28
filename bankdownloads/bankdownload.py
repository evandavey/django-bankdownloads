import os
import hashlib
import time
import re
from bankdownloads.ofx import *
from bankdownloads.bankcsv import BankCSV

class BankDownload:
    """
    An object to represent a bank download of transactions
    """

    
    #Standard csv output headers
    header=[['TransId','FileType','AccountId','Date','Payee','Memo','Value','Currency','FXCurrency','FXAmount','FXRate']]
    
    def __init__(self, path):
        self.path = path
        self.data=[]
        self.accountid=''
        self.bankid=''
        self.SetFileType()
    
    #custom print
    def __repr__(self):
        
        ostr="::Bank Download::"+"\n"
        ostr+="Path: " + self.path +"\n"
        ostr+="Type: " + self.filetype +"\n"
        ostr+="Bank id: " + self.bankid +"\n"
        ostr+="Account id: " + self.accountid +"\n"
        ostr+="Start Date: " + self.mindate +"\n"
        ostr+="End Date: " + self.maxdate +"\n"
        ostr+="Rows: " + str(len(self.data)) +"\n"
        ostr+="Md5: %s" % str(self.md5()) +"\n"
        return ostr
    
    def SetFileType(self):
        extension = os.path.splitext(self.path)[1]
        
        if extension == ".ofx" or extension == ".qfx":
            self.filetype = "ofx"
        else:
            self.filetype = "csv"
    
    def printdata(self):
        
        for row in self.data:
            print row
    
    #generate a filename for output based on attributes
    def generatefilename(self):
        
        fname = self.bankid+"_"+self.accountid
        fname = self.maxdate+"_"+fname
        
        return fname
        
    def md5(self):
        md5 = hashlib.md5()
        with open(self.path,'rb') as f: 
            for chunk in iter(lambda: f.read(128*md5.block_size), ''): 
                md5.update(chunk)
        return md5.hexdigest()
    
    def writecsv(self,path):
        ofile  = open(path, "w")
        writer = csv.writer(ofile,quoting=csv.QUOTE_NONNUMERIC)

        
        #print header
        writer.writerow(self.data[0].keys())
        
        for row in self.data:
            
            rowd=[]
            for r in row.keys():
                rowd.append(row[r])
            
            writer.writerow(rowd)
        ofile.close()
        print "Created csv: " + path
    
    def writeofx(self,path):
        ofxexport(path,self.data)
        print "Created ofx: " + path
    
    def load(self):
        #print "Loading..."
        if self.filetype == "ofx":
            #print "Loading ofx..."
            r=self.loadofx()
        else:
            #print "Loading csv..."
            r=self.loadcsv()
        
        if r:
            #print "Load failed"
            return r
        
        #print "Processing loaded data...."

        
        if self.bankid == '':
            self.SetBankIdFromPath()
         
        if self.accountid == '':
            self.SetAccountIdFromPath()   
       
        self.SetMaxDate()
        self.SetMinDate()
        self.processdata()
    
    def SetBankIdFromPath(self):
        if self.bankid == '':
            fname=os.path.basename(self.path)
            self.bankid=fname.split("-")[0]

    def SetAccountIdFromPath(self):
        if self.accountid == '':
            fname=os.path.basename(self.path)
            self.accountid=fname.split("-")[1]
    
    def loadofx(self):
        print "Loading data from " + self.path
        ofx = OfxParser.parse(file(self.path))
        #self.data=self.header

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

            
                self.accountid=accid
                self.bankid=bankid
            
                curr=cleanStr(ofx.bank_account.currency)
            
                transid=hashlib.md5(transid+accid+dt+desc+str(val)).hexdigest()
            
                #defaults to be overridden in subclass
                fxrate=1
                fxcurr=curr
                fxamount=val
            
                self.data.append({"transid":transid,"bankid":bankid,"accountid":accid,"date":dt,"payee":payee,"memo":memo,"value":val,"currency":curr,"fxcurrency":fxcurr,"fxamount":fxamount,"fxrate":fxrate})
        
            return 0
        except:
            print 'Could not read ofx'
            return 1
    
    def loadcsv(self):
        
        #print self.path
        b=BankCSV(self.path)
        b.load()
        #print b.GetData()
        self.data=b.GetData()
        self.accountid=b.GetAccountId()
        
        return 0
    
    def processdata(self):

        
        for idx in range(1,len(self.data)):
            
            desc=self.data[idx]["memo"]
            amount=self.data[idx]["value"]

            
            #Foreign Currency Parse
            #HSBC UK Format XXX ZZZ.ZZ @ A.SSSS
            
            p = re.compile('\w{3}\s\d+.\d{2}\s@\s\d+.\d{4}')
            m = re.search(p, desc)
            
            if m:
                fxcurr=desc[m.start():m.start()+3]
                p=re.compile('@\s\d+.\d{4}')
                fxrate=re.search(p,m.group()).group()[2:]
                p=re.compile('\d+.\d{2}')
                fxamount=re.search(p,m.group()).group()
                
                fxamount=float(fxamount)
                fxrate=float(fxrate)
                
                self.data[idx]["fxamount"]=round(fxamount,2)
                self.data[idx]["fxrate"]=round(fxrate,4)
                self.data[idx]["fxcurrency"]=fxcurr

            
            #HSBC Aus Format for FX VISA XXX
            p = re.compile('VISA\s\w{3}\s\d+.\d{2}')
            m = re.search(p, desc)
            
            if m:
                fxcurr=desc[m.start()+5:m.start()+8]
                fxamount=float(desc[m.start()+9:m.end()])
                fxrate=round(fxamount/abs(float(amount)),4)
                self.data[idx]["fxamount"]=round(fxamount,2)
                self.data[idx]["fxrate"]=round(fxrate,4)
                self.data[idx]["fxcurrency"]=fxcurr
    
    def SetMaxDate(self):
        
        self.maxdate='0'
        for row in self.data:
            
            dt=row["date"]
            
            if dt>=self.maxdate:
                self.maxdate=dt
    
    def SetMinDate(self):
        
        self.mindate='999999999'
        for row in self.data:
            dt=row["date"]
            
            if dt<=self.mindate:
                self.mindate=dt

def cleanStr(str):
    
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    str=''.join(c for c in str if c in valid_chars)
    
    return str



def parseDate(dt):
    
    dt=dt.strip()
    
    if len(dt) == 14:
        dt = time.strptime(dt, "%Y%m%d000000")
    else:
        dt = time.strptime(dt, "%Y%m%d")
    
    dt = time.strftime("%Y%m%d", dt)
    return dt
    


