from django.db import models

class BankTransaction(models.Model):
    class Meta:
        app_label = "bankdownloads"
        
    download = models.ForeignKey("BankDownload")    
    date = models.DateField()
    memo = models.CharField(max_length=255)
    payee = models.CharField(max_length=255)
    value = models.DecimalField(decimal_places=2)
    transid = models.CharField(max_length=255)
    
    def __unicode__(self):
        return "Transaction: %(date)s" % globals()
    