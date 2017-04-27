# Import smtplib to provide email functions
import smtplib
import zipfile

# Import the email modules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import mylib as ml #user-defined

config = ml.read_config()

name = 'sendmail'
logfile = 'mail'
logger = ml.init_logging(name,logfile)



try:
  	      
  # Define SMTP email server details
  smtp_server = config.get("SMTP", "smtp_server")
  smtp_port   = int(config.get("SMTP", "smtp_port"))


  # Define User details
  UserId = config.get("UserDetails", "UserId")
  FullName = config.get("UserDetails", "FullName")
  EmailId = config.get("UserDetails", "EmailId")
  ContactNo = config.get("UserDetails", "ContactNo")

  # Define Zip details
  z_directory = '/var/www/logs/'
  z_extractpath = '/var/www/zip/'  
  z_filename = UserId +'_logs.zip'

  # Define email addresses to use
  to_Addr = config.get("SMTP", "to_Addr")

  from_Addr = config.get("SMTP", "from_Addr")
  from_Pass = config.get("SMTP", "from_Pass")

  msg_Sub = config.get("SMTP", "msg_Sub") 
  
  config = ' SMTP Details > Server: ' + str(smtp_server) + ' Port:' + str(smtp_port) + ' 	Mail Details > To: ' + str(to_Addr)+ ' From:	' + str(from_Addr) + ' Sub:	' + str(msg_Sub)
  logger.warning('sendmail has started with config. >> ' + config)
	
  # Construct email
  msg = MIMEMultipart('alternative')
  msg['To'] = to_Addr
  msg['From'] = from_Addr
  msg['Subject'] = msg_Sub + " : " + FullName
  
  #read database            
  logger.info('checkfeedback')
  #######################Query to check whether a record exists in table#######################
  checkfeedback = "select count(*) from feedback WHERE issend=0;"
  logger.debug(checkfeedback)
  count = ml.db_fetchone(checkfeedback)
  logger.info('executed')  
  logger.debug('count >> ' + str(count))
  #######################Query to check whether a record exists in table#######################

  if count!=0: #records exists go with updation
     logger.info('*-*Records Found*-*')

     logger.info('getfeedback')
     getfeedback = "select * from feedback WHERE issend=0 ORDER BY inserted_date asc;"
     logger.debug(getfeedback)
     cursor = ml.db_fetchall(getfeedback)
     logger.info('executed') 

     attachcount = 0
     for row in cursor:          
          message = row[0]
          isattach = row[1]
          time = row[2]
          
          logger.info('Email Body') 
          logger.debug('message >> ' + message)          
          logger.debug('isattach >> ' + str(isattach))

          
          if isattach==1:
            attachcount = attachcount + 1                  
          
          if attachcount==1:
            config = ' Directory: ' + z_directory + ' Extract Path: ' + z_extractpath + ' File Name: '  + z_filename            
            logger.warning('Create Zip Only Once with config. >> ' + config)

            # Zip Section
            zipf = zipfile.ZipFile(z_extractpath + z_filename, 'w', zipfile.ZIP_DEFLATED)
            ml.zipdir(z_directory, zipf)
            zipf.close()            
            dirsize = ml.get_dirsize(z_directory)
            logger.debug('Actual Directory Size : ' + str(dirsize))                        
            zipsize = ml.get_filesize(z_extractpath,z_filename)
            logger.debug('Compressed Size : ' + str(zipsize))            
            logger.info('executed')                        
            # Zip Section
            
          html = """\
          <html>
                    <head></head>
                    <body>
                                    <p>Hello!</p> 
                                    <p>"""+message+"""</p>
                                    <p>Regards,<br>"""+FullName+""" | Beymax User <br>UserId : <b> """+UserId+"""</b><br>Contact : <a href="tel:"""+ContactNo+"""">"""+ContactNo+"""</a> <br>Email : <a href="""+EmailId+""">"""+EmailId+"""</a></p>                  
                    </body>
          </html>
          """
          #print (html)
          
          # Record the MIME types of both parts - text/plain and text/html.
          part = MIMEText(html, 'html')

          # Attach parts into message container.
          # According to RFC 2046, the last part of a multipart message, in this case
          # the HTML message, is best and preferred.

          msg.attach(part)

          if isattach==1:
            # This is the binary part(The Attachment):
            part = MIMEApplication(open(z_extractpath + z_filename,"rb").read())
            part.add_header('Content-Disposition', 'attachment', filename=z_filename)
            msg.attach(part)

          server=smtplib.SMTP(smtp_server, smtp_port)
          server.starttls()

          server.login(from_Addr, from_Pass)
          server.sendmail(from_Addr, to_Addr, msg.as_string())

          
          print ('Email sent!')
          logger.info('Email sent!')

          logger.info('updatefeedback')        
          updatefeedback = "update feedback set "  ;
          updatefeedback  =  updatefeedback + "issend=1 , send_date = datetime('now', 'localtime') WHERE ";
          updatefeedback  =  updatefeedback + "message='"+  message +"' ;";
          logger.debug(updatefeedback)                                        
          ml.db_execquery(updatefeedback)
          logger.info('executed')
          #######################Update Query#######################

     logger.info('**AttachCount**')    
     logger.debug('attachcount >> ' + str(attachcount))
  else:
     logger.info('No Records found!')

  logger.warning('sendmail has stopped << ')
except:  
  logger.exception("got error")
  logger.critical('senmail has stopped unexpectedly!!! <<')
