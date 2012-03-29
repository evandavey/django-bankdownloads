from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os,shutil
from traceback import print_exc
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist

from bankdownloads.models import BankDownload

class Command(BaseCommand):
    args = 'import dir'
    help = 'Processes and imports new bank downloads'

    def handle(self, *args, **options):

        try:
            srchpath = settings.BANKDOWNLOADS_IMPORT_PATH
            srchpath = os.path.join('',srchpath)
        except AttributeError:
            raise CommandError('Please set BANKDOWNLOADS_IMPORT_PATH in settings')
            
        fileExtList=[".csv",".ofx",".qfx"]


        self.stdout.write("Searching: %s\n" % srchpath)
        
        if not os.path.exists(srchpath): 
            raise CommandError("Search path %s does not exist" % srchpath)

               

        files=os.listdir(srchpath) 
        for f in files:
            try:

                if os.path.splitext(f)[1] in fileExtList:
                    
                    fh=open(os.path.join(srchpath,f),mode='rb')
                    nb=BankDownload()
                    nb.original_file_name=f
                    nb.original_file=File(fh)
                    checksum=nb.generate_checksum()
                    doUpdate=True
                    try:
                        
                        b=BankDownload.objects.get(original_file_name=f)
                     
                        if checksum==b.checksum:
                            doUpdate=False
                            print "Skipping %s" % f
                        else:
                            doUpdate=True
                    except ObjectDoesNotExist:
                        pass
                    except:
                        print_exc()
                   
                    if doUpdate:                     
                        try:
                            nb.save()
                        except:
                            print "Skipping %s" % f
                        fh.close()
                        
                        
                   
                        
            
           
            
            except:
                
                print_exc()
                raise CommandError("Someting unknown went wrong")
                
                

       #verbosity = options.get('verbosity', 1)
    
        # if len(args) < 1:
        #           raise CommandError('Requires arguments %s' % self.args)
        #         
        
          