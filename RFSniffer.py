#!/usr/bin/env python

import time
import pigpio
import vw
import sys
import traceback

import os
import subprocess
import mylib as ml #user-defined

config = ml.read_config()
  
name = 'RFSniffer'
logfile = 'debug'
logger = ml.init_logging(name,logfile)
  
name = 'rdd'
logfile = 'rdd'
logger1 = ml.init_logging(name,logfile)
  
name = 'MotionDetect'
logfile = 'motion'
logger2 = ml.init_logging(name,logfile)
  
try:  
   
  RX=int(config.get("vw", "RX"))
  TX=int(config.get("vw", "TX_RF"))
  BPS=int(config.get("vw", "BPS"))

  pi = pigpio.pi() # Connect to local Pi.

  rx = vw.rx(pi, RX, BPS) # Specify Pi, rx GPIO, and baud.
  tx = vw.tx(pi, TX, BPS) # Specify Pi, tx GPIO, and baud.
  
  n = 3
  msg = 0

  start = time.time()

  config = ' TX:' + str(TX) + ' RX:' + str(RX) + ' BPS:' + str(BPS)
  logger.warning('RFSniffer has started with config. >> ' + config)

  logger1.warning('RFSniffer has started >> ')

  caltemp = "";#testing

  while (time.time()-start) > 0:

    while not tx.ready():
      time.sleep(0.02)
	
      time.sleep(0.1)

    while not tx.ready():
      time.sleep(0.02)

      time.sleep(0.1)

    while rx.ready():
        rvalue = ("".join(chr (c) for c in rx.get()))
        rvalue_len = len(rvalue)
            
        print(rvalue)
        logger.debug('rvalue : ' + rvalue + ' length : ' + str(rvalue_len))         
       
        if rvalue_len==11: #Code with ACK recieved from rpi (Valid)
     
         #Extraction of Details from rvalue
         user_id = (rvalue[0:3])
         room_no = str(int((rvalue[3:5])))
         d_type = (rvalue[5:7])
         no = (rvalue[7:8])      
         status_code = (rvalue[8:10])    
         #Extraction of Details from rvalue 
                   
         details = 'user_id:' + user_id + ' room_no:' + room_no + ' d_type:' + d_type + ' no:' + no + ' status_code:' + status_code 
         logger.debug('details >> ' + details)
              
         code_valid = False
         logger.info('code validity check >>')
         code_valid = True if ml.check_int(user_id,room_no,d_type,no,status_code) else False
         
         if(code_valid==True): 
          #######################Query to check whether a give table exists in db if not create new table#######################
          #-----------------------------To Check Table Exists new logic-------------------------------------------#
          logger.debug('tablesql')
          tablesql = "SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND "  ;
          tablesql  =  tablesql + "name='room" + room_no +"_log';";            
          logger.debug(tablesql)
              
          count = ml.db_fetchone(tablesql)
          logger.info('executed')
          logger.debug('count >> ' + str(count))
              
          if count==0: #table does not exists go with creation
           logger.info('new log table creation : newtablesql')
           #######################new Table Creation#######################
           newtablesql = "CREATE TABLE room" + room_no +"_log";
           newtablesql  = newtablesql + " (userid int, room int, type int, no int, status int, inserted_date datetime);";         
           logger.debug(newtablesql)
            
           ml.db_execquery(newtablesql)
           logger.info('executed')
           #######################new Table Creation#######################
            
           #######################Insert entry in table Rooms#######################         
           logger.info('new entry in rooms : insertentry')
               
           insertentry = "insert into rooms (room ,name ,alias ,isactive ,islog ,inserted_date ,updated_date) values ("  ;
           insertentry  =  insertentry + room_no +",'room"+room_no+"','room"+room_no+"',1,1,datetime('now', 'localtime'),datetime('now', 'localtime'));";         
           logger.debug(insertentry)
               
           ml.db_execquery(insertentry)
           logger.info('executed')
         #######################Insert entry in table Rooms#######################
               
         #------------------------------------------------------------------------#
         #######################Query to check whether a give table exists in db if not create new table#######################
          if d_type=="07" : #Motion
             logger2.info('*--------*Motion Detection*--------*')
             print('*--------*Motion Detection*--------*')
             logger2.info('checksql')
             #######################Query to check whether a record exists in table#######################
             checksql = "SELECT EXISTS (select * from motion WHERE "  ;
             checksql  =  checksql + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +");";             
             logger2.debug(checksql)
                     
             count = ml.db_fetchone(checksql)
             logger2.info('executed')
             logger2.debug('count >> ' + str(count))
             #######################Query to check whether a record exists in table#######################

             if count==1: #record already exists go with updation

                     if status_code == "10":
                       logger2.info('detectionoff')
                       detectionoff = "update motion set "  ;
                       detectionoff  =  detectionoff + "status ="+  status_code + " , updated_date = datetime('now', 'localtime') WHERE ";
                       detectionoff  =  detectionoff + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
                       logger2.debug(detectionoff)
                                      
                       ml.db_execquery(detectionoff)
                       logger2.info('executed')
                     elif status_code == "11":
                       logger2.info('detectionon')
                       detectionoff = "update motion set "  ;
                       detectionoff  =  detectionoff + "status ="+  status_code + " , updated_date = datetime('now', 'localtime') WHERE ";
                       detectionoff  =  detectionoff + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
                       logger2.debug(detectionoff)
                                      
                       ml.db_execquery(detectionoff)
                       logger2.info('executed')                       
                     elif status_code == "13":
                       logger2.info('nomoredetection')
                       nomoredetection = "update motion set "  ;
                       nomoredetection  =  nomoredetection + "status ="+  status_code + " , updated_date = datetime('now', 'localtime') WHERE ";
                       nomoredetection  =  nomoredetection + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
                       logger2.debug(nomoredetection)
                                      
                       ml.db_execquery(nomoredetection)
                       logger2.info('executed')                     
                     else:
                       print('else Motion status_code : ' + status_code)
                       logger2.info('checkrunning')                                          
                       
                       #######################Query to check whether a record is running in background#######################
                       checkrunning = "SELECT EXISTS (select * from motion WHERE "  ;
                       checkrunning  =  checkrunning + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +"  AND isrunning = 1);";             
                       logger2.debug(checkrunning)
                               
                       count = ml.db_fetchone(checkrunning)
                       logger2.info('executed')
                       logger2.debug('count >> ' + str(count))

                       if count==1: #record already is already in running state                                                  
                         logger2.warning('ALREADY RUNNING : python motiondetect.py 60 ')
                         print('ALREADY RUNNING : python motiondetect.py 60 ')

                         print('updaterunning')
                         logger2.info('updaterunning')
                         updaterunning = "update motion set "  ;
                         updaterunning  =  updaterunning + "status = 12 , updated_date = datetime('now', 'localtime') WHERE ";
                         updaterunning  =  updaterunning + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
                         logger2.debug(updaterunning)
                                        
                         ml.db_execquery(updaterunning)
                         logger2.info('executed')
                       else:
                         print('insertrunning')
                         logger2.info('insertrunning')
                         #######################Update Query#######################
                         insertrunning = "update motion set "  ;
                         insertrunning  =  insertrunning + "status ="+  status_code + " , isrunning = 1, start_date = datetime('now', 'localtime'), updated_date = datetime('now', 'localtime') WHERE ";
                         insertrunning  =  insertrunning + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
                         logger2.debug(insertrunning)
                                        
                         ml.db_execquery(insertrunning)
                         logger2.info('executed')
                         #os.popen('sudo python codesend.py 1010101111')
                         logger.warning('python motiondetect.py '+rvalue+' 60')
                         p = subprocess.Popen('python motiondetect.py '+rvalue+' 60', shell = True)                                                  
                         #######################Update Query#######################   
                     
             else: #record does not exists go with insertion
                            logger.info('insertsql')
                            #######################Insert Query#######################
                            insertsql = "insert into motion (userid, room, type, no, status, inserted_date, updated_date) values ("  ;
                            insertsql  =  insertsql + user_id +"," + room_no +"," + d_type +"," + no +"," + status_code +",datetime('now', 'localtime'),datetime('now', 'localtime'));";
                            logger.debug(insertsql)
                                            
                            ml.db_execquery(insertsql)
                            logger.info('executed')
                            #######################Insert Query#######################
          elif d_type=="13": #Water           
             logger.info('*--------*Water Level Reading*--------*')
          elif d_type=="14" : #Temperature 
            #######################Insert Temperature#######################            
             logger.info('*--------*Temperature Reading*--------*')
              
             caltemp = status_code +"." + no;

             logger.info('checkroomtemp')
             #######################Query to check whether a record exists in table#######################
             checkroomtemp = "SELECT EXISTS (select * from temps WHERE roomno=" + room_no +" );";                         
             logger.debug(checkroomtemp)
                     
             count = ml.db_fetchone(checkroomtemp)
             logger.info('executed')
             logger.debug('count >> ' + str(count))

             if count==1: #record already exists go with updation                     
                       logger.info('updateroomtemp')
                       
                       updateroomtemp = "update temps set "  ;
                       updateroomtemp  =  updateroomtemp + "temp ="+  caltemp + " , timestamp = datetime('now', 'localtime') WHERE ";
                       updateroomtemp  =  updateroomtemp + " roomno=" + room_no +" ;";
                       logger.debug(updateroomtemp)
                      
                       ml.db_execquery(updateroomtemp)
                       logger.info('executed')
             else:
                       logger.info('insertroomtemp')
                       
                       insertroomtemp = "insert into temps (roomno, temp,timestamp) values ("  ;
                       insertroomtemp  =  insertroomtemp + room_no +"," + caltemp +",datetime('now', 'localtime'));";            
                       logger.debug(insertroomtemp)
                                
                       ml.db_execquery(insertroomtemp)
                       logger.info('executed')           
            #######################Insert Temperature#######################
          elif d_type=="15" : #Humidity
              #######################Insert Humidity#######################            
              logger.info('*--------*Humidity Reading*--------*')
                      
              calhumi = status_code +"." + no;

              logger.info('checkroomhumi')
              #######################Query to check whether a record exists in table#######################
              checkroomhumi = "SELECT EXISTS (select * from humis WHERE roomno=" + room_no +" );";                         
              logger.debug(checkroomhumi)
                     
              count = ml.db_fetchone(checkroomhumi)
              logger.info('executed')
              logger.debug('count >> ' + str(count))

              if count==1: #record already exists go with updation                     
                       logger.info('updateroomhumi')
                       
                       updateroomhumi = "update humis set "  ;
                       updateroomhumi  =  updateroomhumi + "humi ="+  calhumi + " , timestamp = datetime('now', 'localtime') WHERE ";
                       updateroomhumi  =  updateroomhumi + " roomno=" + room_no +" ;";
                       logger.debug(updateroomhumi)
                      
                       ml.db_execquery(updateroomhumi)
                       logger.info('executed')
              else:
                       logger.info('insertroomhumi')
                       
                       insertroomhumi = "insert into humis (roomno, humi,timestamp) values ("  ;
                       insertroomhumi  =  insertroomhumi + room_no +"," + calhumi +",datetime('now', 'localtime'));";            
                       logger.debug(insertroomhumi)
                                
                       ml.db_execquery(insertroomhumi)
                       logger.info('executed')                      
              
              logger1.info('RDDTool section start')
              logger1.info('Building param : ') #testing
              name = 'temperature_perhour.rrd'
              param = 'N:'+ caltemp +':' +calhumi #testing
              logger1.debug(param) #testing
              logger1.info('update_rdd >> name ' + name)              
              ml.update_rdd('temperature_perhour.rrd', param); #testing
              logger1.info('executed')
              
              logger1.warning('#####################TEMPEARTURE#####################')

              fetch_temp1 = "select temp from temps WHERE roomno=1;";
              logger.debug(fetch_temp1)
                     
              temp1 = ml.db_fetchone(fetch_temp1)
              logger.info('executed')
              logger.debug('temp1 >> ' + str(temp1))

              fetch_temp2 = "select temp from temps WHERE roomno=2;";
              logger.debug(fetch_temp2)
                     
              temp2 = ml.db_fetchone(fetch_temp2)
              logger.info('executed')
              logger.debug('temp2 >> ' + str(temp2))
              
              logger1.info('Building param : ')
              name = 'temperature.rrd'
              param = 'N:'+ str(temp1) +':' + str(temp2)
              logger1.debug(param)
              logger1.info('update_rdd >> name ' + name)              
              ml.update_rdd(name, param);
              logger1.info('executed')              
              logger1.warning('#####################TEMPEARTURE#####################')
              
              logger1.warning('#####################HUMIDITY#####################')

              fetch_humi1 = "select humi from humis WHERE roomno=1;"; 
              logger.debug(fetch_humi1)
                     
              humi1 = ml.db_fetchone(fetch_humi1)
              logger.info('executed')
              logger.debug('humi1 >> ' + str(humi1))

              fetch_humi2 = "select humi from humis WHERE roomno=2;"; 
              logger.debug(fetch_humi2)
                     
              humi2 = ml.db_fetchone(fetch_humi2)
              logger.info('executed')
              logger.debug('humi2 >> ' + str(humi2))
              
              logger1.info('Building param : ')
              name = 'humidity.rrd'
              param = 'N:'+ str(humi1) +':' + str(humi2)
              logger1.debug(param) 
              logger1.info('update_rdd >> name ' + name)              
              ml.update_rdd(name, param);
              logger1.info('executed')              
              logger1.warning('#####################HUMIDITY#####################')
              
              logger1.info('RDDTool section end!')
              #######################Insert Humidity#######################
          else: #DeviceStat
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
                       updatesql  =  updatesql + "status ="+  status_code + " , updated_date = datetime('now', 'localtime') , ack = 1 WHERE ";
                       updatesql  =  updatesql + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
                       logger.debug(updatesql)
                                      
                       ml.db_execquery(updatesql)
                       logger.info('executed')
                       #######################Update Query#######################

                       logger.info('insertlog')
                       #######################Insert Log#######################
                       insertlog = "insert into room" + room_no +"_log (userid, room, type, no, status,inserted_date) values ("  ;
                       insertlog  =  insertlog + user_id +"," + room_no +"," + d_type +"," + no +"," + status_code +",datetime('now', 'localtime'));";
                       
                       ml.db_execquery(insertlog)
                       logger.info('executed')
                       #######################Insert Log######################
               else: #record does not exists go with insertion
                              logger.info('trigger update from device : insertsql')
                              #######################Insert Query#######################
                              insertsql = "insert into devicestat (userid, room, type, no, status,updated_date) values ("  ;
                              insertsql  =  insertsql + user_id +"," + room_no +"," + d_type +"," + no +"," + status_code +",datetime('now', 'localtime'));";
                              logger.debug(insertsql)
                                              
                              ml.db_execquery(insertsql)
                              logger.info('executed')
                              #######################Insert Query#######################

                              logger.info('insertlog')
                              #######################Insert Log#######################
                              insertlog = "insert into room" + room_no +"_log (userid, room, type, no, status,inserted_date) values ("  ;
                              insertlog  =  insertlog + user_id +"," + room_no +"," + d_type +"," + no +"," + status_code +",datetime('now', 'localtime'));";
                                               
                              ml.db_execquery(insertlog)
                              logger.info('executed')
                              #######################Insert Log######################
         else:         
          logger.info('Invalid Code')
            
         
        elif len(rvalue)==10 : # Code is Recieved from Web        
          logger.info('Recieved from WEB PAGE')
        else: # Code is Invalid        
          logger.info('Invalid Code Length')
      
      #conn.close() #conn close
      
  rx.cancel() # Cancel Virtual Wire receiver.

  pi.stop() # Disconnect from local Pi.

  #logger.warning('RFSniffer has stopped <<')
  #logger1.warning('RFSniffer has stopped <<')

 
    
except:
    logger.exception("got error")
    logger.critical('RFSniffer has stopped unexpectedly!!! <<')
