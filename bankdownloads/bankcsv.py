import csv
import sys
import hashlib
import time
import os

#Parent class that defines basic attributes and methods for BankCSV files
class BankCSV:

   

    def __init__(self,path):
        self.bankid = ""
        self.path = path
        self.data =[]
        self.accountid = ""

    def __repr__(self):

        ostr="Name:"+self.bankid+"\n"
        ostr+="Acc:"+self.accountid+"\n"
        ostr+="Path:"+self.path+"\n"

        self.printdata()

        return ostr

    def wipeclear(self):
        
        print "wiping " + self.bankid
        self.bankid=''
        self.path=''
        self.accountid=''
        del self.data[:]
    
    def GetData(self):
        return self.data

    def GetAccountId(self):
        return self.accountid

    def GetBankId(self):
        return self.bankid

    def printdata(self):

        for row in self.data:
            print row
            
    def GetAccountIdFromPath(self):
        
        try:
            
            filename=self.path
            filename=os.path.basename(self.path)
            return filename.split('-')[1]
        
        except:
            return ""

    def GetAccountIdRabo(self):
        
        ofile  = open(self.path, "r")
        reader = csv.reader(ofile)
        header=reader.next()
        accid=''
        if len(header) == 3:
            accid=header[1]
            accid=accid.replace("-","")
        
        
        return accid
        ofile.close()
        
    
    def format_val(self,val):
        
        val=val.strip().replace('$','').replace(',','')
        
	if val:
        	val=float(val)
		return val
	else:
		return 0

    def load(self):
        
        # data definitions
        csvs=[
           {'bankid':'CBACashManagement',
           'header': ['Date','Description','Debit($)','Credit($)','Balance($)',''],
           'currency': 'AUD',
           'header_row': 1,
           'data_row': 2,
           'date_col':0,
           'date_format':"%d/%m/%Y",
           'credit_col':3,
           'memo_col': 1,
           'accountid':self.GetAccountIdFromPath()
           },
           {'bankid':'RaboPlus',
           'header': ['Operation number', 'Operation date', 'Description', 'Operation amount', 'Currency', 'Value date', 'Counterparty account', 'Counterparty name :', 'Communication 1 :', 'Communication 2 :', 'Operation reference'],
           'currency': 'AUD',
           'header_row': 2,
           'data_row': 3,
           'date_col':1,
           'date_format':"%d-%m-%Y",
           'credit_col':3,
           'memo_col': 2,
           'payee_col': 6,
           'accountid':self.GetAccountIdRabo(),
           },
           {'bankid':'INGDirect',
           'header': ['Date',' Description',' Debit',' Credit',' Balance'],
           'header_row': 1,
           'currency': 'AUD',
           'data_row': 2,
           'date_col':0,
           'date_format':"%d/%m/%Y",
           'credit_col':3,
           'debit_col':2,
           'memo_col': 1,
           'accountid':self.GetAccountIdFromPath(),
           },
           {'bankid':'FSFSuper',
           'header': ['Transaction Date','Payroll End Date','Employer','Transaction Type','Investment Option','Transaction Units','Unit Price','Transaction Amount'],
           'header_row': 1,
           'currency': 'AUD',
           'data_row': 2,
           'date_col':0,
           'date_format':"%d/%m/%Y",
           'credit_col':7,
           'memo_col': 3,
           'accountid':self.GetAccountIdFromPath(),
           },
        ]
        
        for c in csvs:
            f  = open(self.path, "r")
            reader = csv.reader(f)
            
            for i in range(0,c['header_row']):
                try:
                    header=reader.next()
                except:
                    continue
                i=i+1
            
   
            if header == c['header']:
                self.bankid=c['bankid']
                self.accountid=c['accountid']
                print "....found csv for %s,%s" % (self.bankid,self.accountid)
                                
                for row in reader:
                    if len(row)==0:
                        continue
                        
                    dt=row[c['date_col']]
                    dt = time.strptime(dt, c['date_format'])
                    dt = time.strftime("%Y%m%d", dt)

                    curr=c['currency']
                    fxcurr=curr
                    fxrate=1
                    
                    try:
                        payee=row[c['payee_col']].strip()
                    except:
                        payee=""
                        
                    try:
                        memo=row[c['memo_col']].strip()
                    except:
                        memo=""

                    try:
                        debit=abs(self.format_val(row[c['debit_col']]))*-1
                        debit=float(debit)
                    except:
                        print 'Error reading debit'
                        debit=0.0

                    try:
                        credit=abs(self.format_val(row[c['credit_col']]))
                        credit=float(credit)

                    except:
                        print 'Error reading credit'
                        credit=0.0

                    if (debit):
                        val = round(debit,2)
                    else:
                        val = round(credit,2)
                   
                    fxamount=val

                    transid=hashlib.md5(self.bankid+dt+str(val)+payee+memo).hexdigest()
                    self.data.append({"transid":transid,"bankid":self.bankid,"accountid":self.accountid,"date":dt,"payee":payee,"memo":memo,"value":val,"currency":curr,"fxcurrency":fxcurr,"fxamount":fxamount,"fxrate":fxrate})
                
                f.close()
                return
            f.close()
        print "**NO MATCH**"    
        return
        
