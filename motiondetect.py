import time
import sys
import os

import sys
import traceback

import mylib as ml #user-defined

name = 'MotionDetect'
logfile = 'motion'
logger = ml.init_logging(name,logfile)

try:
      
    mins = 0    
  
    # Only run if the user types in "start"

    # Loop until we reach 20 minutes running
    
    rvalue = sys.argv[1]
    settime = sys.argv[2]
    settime = int(settime)

    #Extraction of Details from rvalue
    user_id = (rvalue[0:3])
    room_no = str(int((rvalue[3:5])))
    d_type = (rvalue[5:7])
    no = (rvalue[7:8])      
    status_code = (rvalue[8:10])    
    #Extraction of Details from rvalue
         
    config =  'user_id:' + str(user_id) + 'room_no:' + str(room_no) + 'd_type:' + str(d_type) + 'no:' + str(no)+ 'status_code:' + str(status_code)+ 'settime:' + str(settime)
    logger.warning('MotionDetect has started with config. >> ' + config)
    
    print settime
    while mins != settime:        
        if mins < settime/2:
            print ">first phase>", mins
            logger.info('>first phase>' + str(mins))
            
            # Sleep for a minute
            time.sleep(1)            
    
           # Increment the minute total        
        elif mins > settime/2:
            print ">second phase>", mins
            logger.info('>second phase>' + str(mins))

            time.sleep(1)
            
            #read database            
            logger.info('checksql')
            #######################Query to check whether a record exists in table#######################
            checksql = "SELECT EXISTS (select * from motion WHERE "  ;
            checksql  =  checksql + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +" AND status=12);";             
            logger.debug(checksql)
                     
            count = ml.db_fetchone(checksql)
            logger.info('executed')
            logger.debug('count >> ' + str(count))
            #######################Query to check whether a record exists in table#######################

            if count==1: #record already exists go with updation
               logger.info('*-*Timer Reset*-*')
               mins = 0 #reset the timer               
               #dump null into database
               logger.info('resettimer')
               #######################Update Query#######################
               resettimer = "update motion set "  ;
               resettimer  =  resettimer + "status =99 , start_date = datetime('now', 'localtime'), updated_date = datetime('now', 'localtime') WHERE ";
               resettimer  =  resettimer + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
               logger.debug(resettimer)
                                
               ml.db_execquery(resettimer)
               logger.info('executed')
               #######################Update Query#######################
            
            
            
            #mins += 1            
            
        mins += 1
        
        if mins == 1:
            logger.info('minchangecode')
            #######################Update Query#######################
            minchangecode = "update motion set "  ;
            minchangecode  =  minchangecode + "status =88 , start_date = datetime('now', 'localtime'), updated_date = datetime('now', 'localtime') WHERE ";
            minchangecode  =  minchangecode + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
            logger.debug(minchangecode)
                                    
            ml.db_execquery(minchangecode)
            logger.info('executed')
            #######################Update Query#######################
        
        if mins == settime:
            print mins
            logger.info(str(mins))
            os.popen('sudo python codesend.py 10101071131')
            #os.popen('sudo python codesend.py 1010101110')
            logger.info('>python codesend.py 10101071131>')
            
            logger.info('stoprunning')
            #######################Update Query#######################
            stoprunning = "update motion set "  ;
            stoprunning  =  stoprunning + "status ="+  status_code + " , isrunning = 0, end_date = datetime('now', 'localtime'), updated_date = datetime('now', 'localtime') WHERE ";
            stoprunning  =  stoprunning + "userid="+  user_id +" AND room=" + room_no +" AND type=" + d_type +" AND no="+ no +";";
            logger.debug(stoprunning)
                            
            ml.db_execquery(stoprunning)
            logger.info('executed')
            #######################Update Query#######################
    
    logger.warning('MotionDetect has stopped <<')
                   
except:
    logger.exception("got error")
    logger.critical('MotionDetect has stopped unexpectedly!!! <<')        
        
