#!/usr/bin/env python

import time
import pigpio
import vw
import sys
import traceback

import mylib as ml #user-defined

config = ml.read_config()

name = 'codesend'
logfile = 'debug'
logger = ml.init_logging(name,logfile)
  
try:
		
  TX=int(config.get("vw", "TX_Code"))
  BPS=int(config.get("vw", "BPS"))

  pi = pigpio.pi() # Connect to local Pi.

  tx = vw.tx(pi, TX, BPS) # Specify Pi, tx GPIO, and baud.
  
  config = ' TX:' + str(TX) + ' BPS:' + str(BPS)
  logger.warning('codesend has started with config. >> ' + config)

  while tx.ready():
   
   #tx.put("{:s}".format(sys.argv[1]))
   
   rvalue = "{:s}".format(sys.argv[1])   
   
   rvalue_len = len(rvalue)
   
   #print(rvalue)
   logger.debug('rvalue : ' + rvalue + ' length : ' + str(rvalue_len))
	 
   if rvalue_len==10: #Code recieved from web (Valid)
   
       #Extraction of Details from Code
       user_id = (rvalue[0:3])
       str_room_no = (rvalue[3:5])
       room_no = str(int((rvalue[3:5])))
       d_type = (rvalue[5:7])
       no = (rvalue[7:8])      
       status_code = (rvalue[8:10])    
       #Extraction of Details from Code  
       
       details = 'user_id:' + user_id + ' room_no:' + room_no + ' d_type:' + d_type + ' no:' + no + ' status_code:' + status_code 
       logger.debug('details >> ' + details)
			 
       if status_code != "99": #To avoid code that is triggered by rpi
            
           logger.info('devicecheck')
	   #######################Query to check whether a record exists in table#######################
           devicecheck = "SELECT EXISTS (select * from revoke WHERE "  ;
           devicecheck  =  devicecheck + "deviceid="+  user_id + str_room_no + d_type + no +" );"
           logger.debug(devicecheck)
					 
           count = ml.db_fetchone(devicecheck)
           logger.info('executed')
           logger.debug('count >> ' + str(count))
           #######################Query to check whether a record exists in table#######################
           if count==1:
             #######################Query to check whether a record exists in table#######################
             logger.info('revokcheck')
             revokcheck = "SELECT EXISTS (select * from revoke WHERE "  ;
             revokcheck  =  revokcheck + "deviceid="+  user_id + str_room_no + d_type + no +" AND ischeck=1 );";           
             logger.debug(revokcheck)
                                           
             count = ml.db_fetchone(revokcheck)
             logger.info('executed')
             logger.debug('count >> ' + str(count))                                           
             #######################Query to check whether a record exists in table#######################
           
             if count==1: #record already exists go with updation             
               logger.info('true')
             else:
               logger.info('false')
               break; 

           tx.put("{:s}".format(sys.argv[1])) #forward to RFSniffer
           logger.info('checksql')
	   #######################Query to check whether a record exists in table#######################
           checksql = "SELECT EXISTS (select * from devicestat WHERE "  ;
           checksql  =  checksql + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +");";           
           logger.debug(checksql)
					 
           count = ml.db_fetchone(checksql)
           logger.info('executed')
           logger.debug('count >> ' + str(count))
					 
           #######################Query to check whether a record exists in table#######################
         
           if count==1: #record already exists go with updation             
             logger.info('updatesql')
						 
             #######################Update Query#######################
             updatesql = "update devicestat set "  ;
             updatesql  =  updatesql + "status ="+  status_code + " , updated_date = datetime('now', 'localtime') , ack = 0  WHERE ";
             updatesql  =  updatesql + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
             logger.debug(updatesql)
             
             ml.db_execquery(updatesql)
             logger.info('executed')
             #######################Update Query#######################
          
           else: #record does not exists go with insertion              
              logger.info('insertsql')
							
              #######################Insert Query#######################
              insertsql = "insert into devicestat (userid, room, type, no, status,updated_date) values ("  ;
              insertsql  =  insertsql + user_id +"," + room_no +"," + d_type +"," + no +"," + status_code +",datetime('now', 'localtime'));";
              logger.debug(insertsql)
              
              ml.db_execquery(insertsql)
              logger.info('executed')
              #######################Insert Query#######################
       else:               
               logger.info('trigger update from rpi')
               tx.put("{:s}".format(sys.argv[1])) #forward to RFSniffer
							 
   elif len(rvalue)==11 : # Code is Recieved from rpi      
      logger.info('Recieved from RPI')
      tx.put("{:s}".format(sys.argv[1])) #forward to RFSniffer
   else: # Code is Invalid      
      logger.info('Invalid Code Length!')
      tx.put("{:s}".format(sys.argv[1])) #forward to RFSniffer
      
   
  while not tx.ready():
   time.sleep(0.02)
   
  tx.cancel() # Cancel Virtual Wire transmitter.

  pi.stop()
  
  logger.warning('codesend has stopped <<')

except:
    logger.exception("got error")
    logger.critical('codesend has stopped unexpectedly!!! <<')    

