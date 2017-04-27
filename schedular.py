from datetime import datetime
from crontab import CronTab
from crontab import CronSlices

import logging
import logging.handlers

import croniter
import sys
import traceback

#import simplejson as json #module installed
import json

import mylib as ml #user-defined

name = 'schedular'
logfile = 'sched'
logger = ml.init_logging(name,logfile)
logger.warning('schedular init >> ')
  
try:  
    
    ##########################INSERT JOB##########################
    def INSERTJOB(p_comment,p_timeslice,p_command,p_devicestat) :         
        logger.info('INSERTJOB')
        logger.debug('p_devicestat : ' + p_devicestat)
				
	#Extraction of Details from p_devicestat
        arr_devicestat = p_devicestat.split('.')
        room = arr_devicestat[0]
        type = arr_devicestat[1]
        no = arr_devicestat[2]
        status = arr_devicestat[3]
	#Extraction of Details from p_devicestat

        commanddetails = 'room:' + room + ' type:' + type + ' no:' + no + ' status:' + status
        logger.debug('command details >> ' + commanddetails)
        jobdetails = 'p_command:' + p_command + ' p_comment:' + p_comment + ' p_timeslice:' + p_timeslice
        logger.debug('job details >> ' + jobdetails)

        logger.info('checkjob')
        #######################Query to check whether a record exists in table#######################
        checkjob = "SELECT EXISTS (select * from schedular WHERE "  ;
        checkjob  =  checkjob + "comment='"+  p_comment + "' AND isdeleted = 0);";
        logger.debug(checkjob)
		   
        count = ml.db_fetchone(checkjob)
        logger.info('executed')
        logger.debug('count >> ' + str(count))
	#######################Query to check whether a record exists in table#######################
				
        if count==1:
            logger.info('JOB ALREADY EXISTS')
            #****$$****JSONDUMP****$$****#
            flag = '0'
            msg = 'Record already Exist'
            Dump = {'flag':flag,'msg':msg}
            logger.debug('dump >> flag:'+flag+',msg:'+msg)
            print json.dumps(Dump)
            #****$$****JSONDUMP****$$****#
            logger.info('JSON dumps')
        else :            
            logger.info('NEW JOB')
            logger.info('CRONTAB section start')
	    #*************************CRONTAB*************************#
            job  = user_cron.new(command=p_command, comment=p_comment)
            job.setall(p_timeslice)
            freq = job.frequency_per_day()
            schedule = job.schedule(date_from=datetime.now())			
            prev_sche = schedule.get_prev()
            next_sche = schedule.get_next()
            #*************************CRONTAB*************************#
            logger.info('CRONTAB section end!')
            
            computeddetails = 'Frequency:' + str(freq) + ' Prev Schedule:' + str(prev_sche) + ' Next Schedule:' + str(next_sche)
            logger.debug('computed details >> ' + computeddetails)
			             
            logger.info('insertjob')
            #######################Insert Query#######################
            insertjob = "insert into schedular (room, type, no, status, command, comment, timeslice, frequency, prev_schedule, next_schedule, inserted_date, updated_date) values ("  ;
            insertjob  =  insertjob +"'"+ room +"','"+ type +"','"+ no +"','"+ status +"','" + p_command+"','" + p_comment +"','" + p_timeslice +"','"+ str(freq) +"','" + str(prev_sche) +"','" + str(next_sche) +"',datetime('now', 'localtime'),datetime('now', 'localtime'));";            
            logger.debug(insertjob)

            ml.db_execquery(insertjob)
            logger.info('executed')
            #######################Insert Query#######################
                                    
            user_cron.write() #Actual write to crontab
            logger.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record added successfully'
            Dump = {'flag':flag,'msg':msg}
            logger.debug('dump >> flag:'+flag+',msg:'+msg)
            print json.dumps(Dump)
            #****$$****JSONDUMP****$$****#
            logger.info('JSON dumps')            
    ##########################INSERT JOB##########################

    ##########################ENABLE JOB##########################
    def ENABLEJOB(p_comment,p_timeslice) :        
        logger.info('ENABLEJOB')
        logger.debug('p_comment : ' + p_comment)
        logger.debug('p_timeslice : ' + p_timeslice)

        logger.info('checkjob')
	#######################Query to check whether a record exists in table#######################
        checkjob = "SELECT EXISTS (select * from schedular WHERE "  ;
        checkjob  =  checkjob + "comment='"+  p_comment + "' AND isactive = 0 AND isdeleted = 0);";        
        logger.debug(checkjob)
		   
        count = ml.db_fetchone(checkjob)
        logger.info('executed')
        logger.debug('count >> ' + str(count))
	#######################Query to check whether a record exists in table#######################
				
        if count==1:            
            logger.info('ENABLING JOB...')
            logger.info('CRONTAB section start')
	    #*************************CRONTAB*************************#
            for job in user_cron.find_comment(p_comment):
                            job.enable(True)
                            job.setall(p_timeslice)                            
                            freq = job.frequency_per_day()
                            schedule = job.schedule(date_from=datetime.now())			
                            prev_sche = schedule.get_prev()
                            next_sche = schedule.get_next()

                            logger.info('enablejob')
                            #######################Update Query#######################
                            enablejob = "update schedular set "  ;
                            enablejob  =  enablejob + "timeslice = '"+ p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , isactive = 1,updated_date = datetime('now', 'localtime') WHERE ";
                            enablejob  =  enablejob + "comment='"+  p_comment +"' AND isdeleted = 0;";
                            logger.debug(enablejob)
                            
                            ml.db_execquery(enablejob)
                            logger.info('executed')
                            #######################Update Query#######################
            #*************************CRONTAB*************************#
            logger.info('CRONTAB section end!')
            
            user_cron.write() #Actual write to crontab
            logger.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record updated successfully'
            Dump = {'flag':flag,'msg':msg}
            logger.debug('dump >> flag:'+flag+',msg:'+msg)
            print json.dumps(Dump)
            #****$$****JSONDUMP****$$****#
            logger.info('JSON dumps')  
        else:
            logger.info('checkjob_enab')
            #######################Query to check whether a record exists in table#######################
            checkjob_enab = "SELECT EXISTS (select * from schedular WHERE "  ;
            checkjob_enab  =  checkjob_enab + "comment='"+  p_comment + "' AND isactive = 1 AND isdeleted = 0);";            
            logger.debug(checkjob_enab)
                       
            count = ml.db_fetchone(checkjob_enab)
            logger.info('executed')
            logger.debug('count >> ' + str(count))
            #######################Query to check whether a record exists in table#######################

            if count==1:                
                logger.info('UPDATING SCHEDULE...')
                logger.info('CRONTAB section start')
                #*************************CRONTAB*************************#
                for job in user_cron.find_comment(p_comment):                            
                                job.setall(p_timeslice)                            
                                freq = job.frequency_per_day()
                                schedule = job.schedule(date_from=datetime.now())			
                                prev_sche = schedule.get_prev()
                                next_sche = schedule.get_next()

                                logger.info('updateschedule')
                                #######################Update Query#######################
                                updateschedule = "update schedular set "  ;
                                updateschedule  =  updateschedule + "timeslice = '"+ p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , updated_date = datetime('now', 'localtime') WHERE ";
                                updateschedule  =  updateschedule + "comment='"+  p_comment +"' AND isdeleted = 0;";
                                logger.debug(updateschedule)
                                
                                ml.db_execquery(updateschedule)
                                logger.info('executed')
                                #######################Update Query#######################
                #*************************CRONTAB*************************#
                logger.info('CRONTAB section end!')          
                user_cron.write() #Actual write to crontab
                logger.info('CRONTAB write')
                #****$$****JSONDUMP****$$****#
                flag = '1'
                msg = 'Record updated successfully'
                Dump = {'flag':flag,'msg':msg}
                logger.debug('dump >> flag:'+flag+',msg:'+msg)
                print json.dumps(Dump)
                #****$$****JSONDUMP****$$****#
                logger.info('JSON dumps')  
            else:                
                logger.info('job not found')        
    ##########################ENABLE JOB##########################
    
    ##########################DISABLE JOB##########################
    def DISABLEJOB(p_comment,p_timeslice) :         
        logger.info('DISABLEJOB')
        logger.debug('p_comment : ' + p_comment)
        logger.debug('p_timeslice : ' + p_timeslice)

        logger.info('checkjob')
	#######################Query to check whether a record exists in table#######################
        checkjob = "SELECT EXISTS (select * from schedular WHERE "  ;
        checkjob  =  checkjob + "comment='"+  p_comment + "' AND isactive = 1 AND isdeleted = 0);";        
        logger.debug(checkjob)
		   
        count = ml.db_fetchone(checkjob)
        logger.info('executed')
        logger.debug('count >> ' + str(count))
	#######################Query to check whether a record exists in table#######################

        if count==1:            
            logger.info('DISABLING JOB...')
            logger.info('CRONTAB section start')
	    #*************************CRONTAB*************************#
            for job in user_cron.find_comment(p_comment):
                            job.enable(False)
                            job.setall(p_timeslice)                                                    
                            freq = job.frequency_per_day()
                            schedule = job.schedule(date_from=datetime.now())			
                            prev_sche = schedule.get_prev()
                            next_sche = schedule.get_next()

                            logger.info('disablejob')
                            #######################Update Query#######################
                            disablejob = "update schedular set "  ;
                            disablejob  =  disablejob + "timeslice = '"+ p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , isactive = 0,updated_date = datetime('now', 'localtime') WHERE ";
                            disablejob  =  disablejob + "comment='"+  p_comment +"' AND isdeleted = 0;";
                            logger.debug(disablejob)
                            
                            ml.db_execquery(disablejob)
                            logger.info('executed')
                            #######################Update Query#######################
            #*************************CRONTAB*************************#								
            logger.info('CRONTAB section end!')          
            user_cron.write() #Actual write to crontab
            logger.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record updated successfully'
            Dump = {'flag':flag,'msg':msg}
            logger.debug('dump >> flag:'+flag+',msg:'+msg)
            print json.dumps(Dump)
            #****$$****JSONDUMP****$$****#
            logger.info('JSON dumps')               
        else:
            logger.info('checkjob_dis')
            #######################Query to check whether a record exists in table#######################
            checkjob_dis = "SELECT EXISTS (select * from schedular WHERE "  ;
            checkjob_dis  =  checkjob_dis + "comment='"+  p_comment + "' AND isactive = 0 AND isdeleted = 0);";            
            logger.debug(checkjob_dis)
                       
            count = ml.db_fetchone(checkjob_dis)
            logger.info('executed')
            logger.debug('count >> ' + str(count))
            #######################Query to check whether a record exists in table#######################

            if count==1:                
                logger.info('UPDATING SCHEDULE...')
                logger.info('CRONTAB section start')
                #*************************CRONTAB*************************#
                for job in user_cron.find_comment(p_comment):                            
                                job.setall(p_timeslice)                            
                                freq = job.frequency_per_day()
                                schedule = job.schedule(date_from=datetime.now())			
                                prev_sche = schedule.get_prev()
                                next_sche = schedule.get_next()

                                logger.info('updateschedule')
                                #######################Update Query#######################
                                updateschedule = "update schedular set "  ;
                                updateschedule  =  updateschedule + "timeslice = '"+ p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , updated_date = datetime('now', 'localtime') WHERE ";
                                updateschedule  =  updateschedule + "comment='"+  p_comment +"' AND isdeleted = 0;";
                                logger.debug(updateschedule)
                                
                                ml.db_execquery(updateschedule)
                                logger.info('executed')
                                #######################Update Query#######################
                #*************************CRONTAB*************************#                            
                logger.info('CRONTAB section end!')          
                user_cron.write() #Actual write to crontab
                logger.info('CRONTAB write')
                #****$$****JSONDUMP****$$****#
                flag = '1'
                msg = 'Record updated successfully'
                Dump = {'flag':flag,'msg':msg}
                logger.debug('dump >> flag:'+flag+',msg:'+msg)
                print json.dumps(Dump)
                #****$$****JSONDUMP****$$****#
                logger.info('JSON dumps')  
            else:                
                logger.info('job not found')  	
    ##########################DISABLE JOB##########################
                
    ##########################FIND JOB##########################
    def FINDJOB(p_comment) :         
        logger.info('FINDJOB')
        logger.debug('p_comment : ' + p_comment)
        
        for job in user_cron.find_comment(p_comment):
            print (job)
    ##########################FIND JOB##########################

    ##########################REMOVE JOB##########################
    def REMOVEJOB(p_comment) :         
        logger.info('REMOVEJOB')
        logger.debug('p_comment : ' + p_comment)
        
        logger.info('checkjob')
        #######################Query to check whether a record exists in table#######################
        checkjob = "SELECT EXISTS (select * from schedular WHERE "  ;
        checkjob  =  checkjob + "comment='"+  p_comment + "' AND isdeleted = 0);";        
        logger.debug(checkjob)
		   
        count = ml.db_fetchone(checkjob)
        logger.info('executed')
        logger.debug('count >> ' + str(count))
	#######################Query to check whether a record exists in table#######################
				
        if count==1:
            logger.info('REMOVING JOB...')
            logger.info('CRONTAB section start')
            #*************************CRONTAB*************************#
            for job in user_cron.find_comment(p_comment):
                if "pi~@$^*" not in job.comment: #To avoid pi Jobs
                    user_cron.remove(job)

                    logger.info('removejob')	
                    #######################Update Query#######################
                    removejob = "update schedular set "  ;
                    removejob  =  removejob + "isdeleted = 1,updated_date = datetime('now', 'localtime') WHERE ";
                    removejob  =  removejob + "comment='"+  p_comment +"';";
                    logger.debug(removejob)
                                          
                    ml.db_execquery(removejob)
                    logger.info('executed')
                    #######################Update Query#######################
                    
	    #*************************CRONTAB*************************#	
            logger.info('CRONTAB section end!')          
            user_cron.write() #Actual write to crontab
            logger.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record deleted successfully'
            Dump = {'flag':flag,'msg':msg}
            logger.debug('dump >> flag:'+flag+',msg:'+msg)
            print json.dumps(Dump)
            #****$$****JSONDUMP****$$****#
            logger.info('JSON dumps')
        else:
            logger.info('job not found')						
    ##########################REMOVE JOB##########################
    		
    ##########################UPDATE JOBS##########################
    def UPDATEJOBS() :         
        logger.info('UPDATEJOBS')
        
        logger.info('UPDATING SCHEDULE FOR ALL JOBS...')
        logger.info('CRONTAB section start')
        #*************************CRONTAB*************************#
        for job in user_cron:
            comment = job.comment            
            logger.debug('comment : ' + comment)

            schedule = job.schedule(date_from=datetime.now())			
            prev_sche = schedule.get_prev()
            next_sche = schedule.get_next()
            
            computeddetails = ' Prev Schedule:' + str(prev_sche) + ' Next Schedule:' + str(next_sche)            
            logger.debug('computed details >> ' + computeddetails)
            
            logger.info('updateschedule')
            #######################Update Query#######################
            updateschedule = "update schedular set "  ;
            updateschedule  =  updateschedule + "prev_schedule = '" + str(prev_sche) +"',next_schedule  = '" + str(next_sche) +"' WHERE ";
            updateschedule  =  updateschedule + "comment='"+  comment +"' AND isactive = 1 AND isdeleted = 0;";            
            logger.debug(updateschedule)
            
            ml.db_execquery(updateschedule)
            logger.info('executed')
            #######################Update Query#######################       
	#*************************CRONTAB*************************#	
        logger.info('CRONTAB section end!')          
        #****$$****JSONDUMP****$$****#
        flag = '1'
        msg = 'All Records updated successfully'
        Dump = {'flag':flag,'msg':msg}
        logger.debug('dump >> flag:'+flag+',msg:'+msg)
        print json.dumps(Dump)
        #****$$****JSONDUMP****$$****#
        logger.info('JSON dumps')		        
    ##########################UPDATE JOBS##########################
    		
    ##########################PRINT ALL JOBS##########################
    def PRINTALLJOBS() :                
        logger.info('PRINT ALL JOBS')
	#*************************CRONTAB*************************#
        for job in user_cron:
            print (job)
	#*************************CRONTAB*************************#
    ##########################PRINT ALL JOBS##########################
    		
    ##########################REMOVE ALL JOBS##########################
    def REMOVEALLJOBS() :         
        logger.info('REMOVEALLJOBS')

        logger.info('REMOVING ALL JOBS...')
        logger.info('CRONTAB section start')
        #*************************CRONTAB*************************#
        for job in user_cron:
            if "pi~@$^*" not in job.comment: 
                user_cron.remove(job)
	#*************************CRONTAB*************************#	
        logger.info('CRONTAB section end!')

        logger.info('removealljob')
        #######################Update Query#######################
        removealljob = "update schedular set ";
        removealljob  =  removealljob + "isdeleted = 1,updated_date = datetime('now', 'localtime');";
        logger.debug(removealljob)

        ml.db_execquery(removealljob)
        logger.info('executed')
	#######################Update Query#######################
        
        user_cron.write() #Actual write to crontab
        logger.info('CRONTAB write')
        #****$$****JSONDUMP****$$****#
        flag = '1'
        msg = 'All Records deleted successfully'
        Dump = {'flag':flag,'msg':msg}
        logger.debug('dump >> flag:'+flag+',msg:'+msg)
        print json.dumps(Dump)
        #****$$****JSONDUMP****$$****#
        logger.info('JSON dumps')
    ##########################REMOVE ALL JOBS##########################


   #-------------------------------------------------------START-------------------------------------------------------------#    
    user_cron = CronTab(user=True)#current user crontab    
    logger.warning('schedular has started with config. >> CronTab(user=True)')
    
    param = "{:s}".format(sys.argv[1])#fetch param
    
    #Extraction of Details from param
    arr_param = param.split(',')
    p_case = arr_param[0]
    #Extraction of Details from param    
		    
    logger.debug('p_case : ' + p_case)

    if(p_case == "1"):
        p_comment = arr_param[1]         
        p_timeslice = arr_param[2]
        p_command = arr_param[3]
        p_devicestat = arr_param[4]        
        INSERTJOB(p_comment,p_timeslice,p_command,p_devicestat)
        #UPDATEJOBS()#UpdateJobs after insert
    elif(p_case == "2"):
        p_comment = arr_param[1]
        p_timeslice = arr_param[2]
        ENABLEJOB(p_comment,p_timeslice)
        #UPDATEJOBS()#UpdateJobs after enable
    elif(p_case == "3"):
        p_comment = arr_param[1]
        p_timeslice = arr_param[2]
        DISABLEJOB(p_comment,p_timeslice)
        #UPDATEJOBS()#UpdateJobs after disable
    elif(p_case == "4"):
        p_comment = arr_param[1]
        FINDJOB(p_comment)
    elif(p_case == "5"):
        p_comment = arr_param[1]
        REMOVEJOB(p_comment)
        #UPDATEJOBS()#UpdateJobs after remove
    elif(p_case == "6"):
        UPDATEJOBS()
    elif(p_case == "7"):
        PRINTALLJOBS()
    elif(p_case == "8"):
        REMOVEALLJOBS()
    
    logger.warning('schedular has stopped <<')
   #-------------------------------------------------------START-------------------------------------------------------------# 
except:
    logger.exception("got error")
    logger.critical('schedular has stopped unexpectedly!!! <<')
    raise
