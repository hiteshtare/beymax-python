# import simplejson as json #module installed
"""This file deals with user's cron tab management"""

import json
import logging
import logging.handlers
import sys
import traceback
from datetime import datetime

import croniter
import mylib as ml  # user-defined
from crontab import CronSlices, CronTab

NAME = 'schedular'
LOG_FILE = 'sched'
LOGGER = ml.init_logging(NAME, LOG_FILE)
LOGGER.warning('schedular init >> ')

try:

    ##########################INSERT JOB##########################
    def insert_job(p_comment, p_timeslice, p_command, p_devicestat):
        """Inserts a new cron job"""
        LOGGER.info('INSERTJOB')
        LOGGER.debug('p_devicestat : ' + p_devicestat)

        # Extraction of Details from p_devicestat
        arr_devicestat = p_devicestat.split('.')
        room = arr_devicestat[0]
        d_type = arr_devicestat[1]
        number = arr_devicestat[2]
        status = arr_devicestat[3]
        # Extraction of Details from p_devicestat

        commanddetails = 'room:' + room + ' type:' + \
            d_type + ' no:' + number + ' status:' + status
        LOGGER.debug('command details >> ' + commanddetails)
        jobdetails = 'p_command:' + p_command + ' p_comment:' + \
            p_comment + ' p_timeslice:' + p_timeslice
        LOGGER.debug('job details >> ' + jobdetails)

        LOGGER.info('checkjob')
        #######################Query to check whether a record exists in table#
        checkjob = "SELECT EXISTS (select * from schedular WHERE "
        checkjob = checkjob + "comment='" + p_comment + "' AND isdeleted = 0);"
        LOGGER.debug(checkjob)

        count = ml.db_fetchone(checkjob)
        LOGGER.info('executed')
        LOGGER.debug('count >> ' + str(count))
        #######################Query to check whether a record exists in table#

        if count == 1:
            LOGGER.info('JOB ALREADY EXISTS')
            #****$$****JSONDUMP****$$****#
            flag = '0'
            msg = 'Record already Exist'
            dump = {'flag': flag, 'msg': msg}
            LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
            print json.dumps(dump)
            #****$$****JSONDUMP****$$****#
            LOGGER.info('JSON dumps')
        else:
            LOGGER.info('NEW JOB')
            LOGGER.info('CRONTAB section start')
            #*************************CRONTAB*************************#
            job = USER_CRON.new(command=p_command, comment=p_comment)
            job.setall(p_timeslice)
            freq = job.frequency_per_day()
            schedule = job.schedule(date_from=datetime.now())
            prev_sche = schedule.get_prev()
            next_sche = schedule.get_next()
            #*************************CRONTAB*************************#
            LOGGER.info('CRONTAB section end!')

            computeddetails = 'Frequency:' + \
                str(freq) + ' Prev Schedule:' + str(prev_sche) + \
                ' Next Schedule:' + str(next_sche)
            LOGGER.debug('computed details >> ' + computeddetails)

            LOGGER.info('insertjob')
            #######################Insert Query#######################
            insertjob = "insert into schedular (room, type, no, status, command, comment, timeslice, frequency, prev_schedule, next_schedule, inserted_date, updated_date) values ("
            insertjob = insertjob + "'" + room + "','" + type + "','" + number + "','" + status + "','" + p_command + "','" + p_comment + "','" + p_timeslice + \
                "','" + str(freq) + "','" + str(prev_sche) + "','" + str(next_sche) + \
                "',datetime('now', 'localtime'),datetime('now', 'localtime'));"
            LOGGER.debug(insertjob)

            ml.db_execquery(insertjob)
            LOGGER.info('executed')
            #######################Insert Query#######################

            USER_CRON.write()  # Actual write to crontab
            LOGGER.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record added successfully'
            dump = {'flag': flag, 'msg': msg}
            LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
            print json.dumps(dump)
            #****$$****JSONDUMP****$$****#
            LOGGER.info('JSON dumps')
    ##########################INSERT JOB##########################

    ##########################ENABLE JOB##########################
    def enable_job(p_comment, p_timeslice):
        """Enables existing cron job"""
        LOGGER.info('ENABLEJOB')
        LOGGER.debug('p_comment : ' + p_comment)
        LOGGER.debug('p_timeslice : ' + p_timeslice)

        LOGGER.info('checkjob')
        #######################Query to check whether a record exists in table#
        checkjob = "SELECT EXISTS (select * from schedular WHERE "
        checkjob = checkjob + "comment='" + p_comment + \
            "' AND isactive = 0 AND isdeleted = 0);"
        LOGGER.debug(checkjob)

        count = ml.db_fetchone(checkjob)
        LOGGER.info('executed')
        LOGGER.debug('count >> ' + str(count))
        #######################Query to check whether a record exists in table#

        if count == 1:
            LOGGER.info('ENABLING JOB...')
            LOGGER.info('CRONTAB section start')
            #*************************CRONTAB*************************#
            for job in USER_CRON.find_comment(p_comment):
                job.enable(True)
                job.setall(p_timeslice)
                freq = job.frequency_per_day()
                schedule = job.schedule(date_from=datetime.now())
                prev_sche = schedule.get_prev()
                next_sche = schedule.get_next()

                LOGGER.info('enablejob')
                #######################Update Query#######################
                enablejob = "update schedular set "
                enablejob = enablejob + "timeslice = '" + p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(
                    prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , isactive = 1,updated_date = datetime('now', 'localtime') WHERE "
                enablejob = enablejob + "comment='" + p_comment + "' AND isdeleted = 0;"
                LOGGER.debug(enablejob)

                ml.db_execquery(enablejob)
                LOGGER.info('executed')
                #######################Update Query#######################
            #*************************CRONTAB*************************#
            LOGGER.info('CRONTAB section end!')

            USER_CRON.write()  # Actual write to crontab
            LOGGER.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record updated successfully'
            dump = {'flag': flag, 'msg': msg}
            LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
            print json.dumps(dump)
            #****$$****JSONDUMP****$$****#
            LOGGER.info('JSON dumps')
        else:
            LOGGER.info('checkjob_enab')
            # Query to check whether a record exists in ta
            checkjob_enab = "SELECT EXISTS (select * from schedular WHERE "
            checkjob_enab = checkjob_enab + "comment='" + \
                p_comment + "' AND isactive = 1 AND isdeleted = 0);"
            LOGGER.debug(checkjob_enab)

            count = ml.db_fetchone(checkjob_enab)
            LOGGER.info('executed')
            LOGGER.debug('count >> ' + str(count))
            # Query to check whether a record exists in ta

            if count == 1:
                LOGGER.info('UPDATING SCHEDULE...')
                LOGGER.info('CRONTAB section start')
                #*************************CRONTAB*************************#
                for job in USER_CRON.find_comment(p_comment):
                    job.setall(p_timeslice)
                    freq = job.frequency_per_day()
                    schedule = job.schedule(date_from=datetime.now())
                    prev_sche = schedule.get_prev()
                    next_sche = schedule.get_next()

                    LOGGER.info('updateschedule')
                    #######################Update Query#######################
                    updateschedule = "update schedular set "
                    updateschedule = updateschedule + "timeslice = '" + p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(
                        prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , updated_date = datetime('now', 'localtime') WHERE "
                    updateschedule = updateschedule + "comment='" + p_comment + "' AND isdeleted = 0;"
                    LOGGER.debug(updateschedule)

                    ml.db_execquery(updateschedule)
                    LOGGER.info('executed')
                    #######################Update Query#######################
                #*************************CRONTAB*************************#
                LOGGER.info('CRONTAB section end!')
                USER_CRON.write()  # Actual write to crontab
                LOGGER.info('CRONTAB write')
                #****$$****JSONDUMP****$$****#
                flag = '1'
                msg = 'Record updated successfully'
                dump = {'flag': flag, 'msg': msg}
                LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
                print json.dumps(dump)
                #****$$****JSONDUMP****$$****#
                LOGGER.info('JSON dumps')
            else:
                LOGGER.info('job not found')
    ##########################ENABLE JOB##########################

    ##########################DISABLE JOB##########################
    def disable_job(p_comment, p_timeslice):
        """Disables existing cron job"""
        LOGGER.info('DISABLEJOB')
        LOGGER.debug('p_comment : ' + p_comment)
        LOGGER.debug('p_timeslice : ' + p_timeslice)

        LOGGER.info('checkjob')
        #######################Query to check whether a record exists in table#
        checkjob = "SELECT EXISTS (select * from schedular WHERE "
        checkjob = checkjob + "comment='" + p_comment + \
            "' AND isactive = 1 AND isdeleted = 0);"
        LOGGER.debug(checkjob)

        count = ml.db_fetchone(checkjob)
        LOGGER.info('executed')
        LOGGER.debug('count >> ' + str(count))
        #######################Query to check whether a record exists in table#

        if count == 1:
            LOGGER.info('DISABLING JOB...')
            LOGGER.info('CRONTAB section start')
            #*************************CRONTAB*************************#
            for job in USER_CRON.find_comment(p_comment):
                job.enable(False)
                job.setall(p_timeslice)
                freq = job.frequency_per_day()
                schedule = job.schedule(date_from=datetime.now())
                prev_sche = schedule.get_prev()
                next_sche = schedule.get_next()

                LOGGER.info('disablejob')
                #######################Update Query#######################
                disablejob = "update schedular set "
                disablejob = disablejob + "timeslice = '" + p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(
                    prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , isactive = 0,updated_date = datetime('now', 'localtime') WHERE "
                disablejob = disablejob + "comment='" + p_comment + "' AND isdeleted = 0;"
                LOGGER.debug(disablejob)

                ml.db_execquery(disablejob)
                LOGGER.info('executed')
                #######################Update Query#######################
            #*************************CRONTAB*************************#
            LOGGER.info('CRONTAB section end!')
            USER_CRON.write()  # Actual write to crontab
            LOGGER.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record updated successfully'
            dump = {'flag': flag, 'msg': msg}
            LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
            print json.dumps(dump)
            #****$$****JSONDUMP****$$****#
            LOGGER.info('JSON dumps')
        else:
            LOGGER.info('checkjob_dis')
            # Query to check whether a record exists in ta
            checkjob_dis = "SELECT EXISTS (select * from schedular WHERE "
            checkjob_dis = checkjob_dis + "comment='" + \
                p_comment + "' AND isactive = 0 AND isdeleted = 0);"
            LOGGER.debug(checkjob_dis)

            count = ml.db_fetchone(checkjob_dis)
            LOGGER.info('executed')
            LOGGER.debug('count >> ' + str(count))
            # Query to check whether a record exists in ta

            if count == 1:
                LOGGER.info('UPDATING SCHEDULE...')
                LOGGER.info('CRONTAB section start')
                #*************************CRONTAB*************************#
                for job in USER_CRON.find_comment(p_comment):
                    job.setall(p_timeslice)
                    freq = job.frequency_per_day()
                    schedule = job.schedule(date_from=datetime.now())
                    prev_sche = schedule.get_prev()
                    next_sche = schedule.get_next()

                    LOGGER.info('updateschedule')
                    #######################Update Query#######################
                    updateschedule = "update schedular set "
                    updateschedule = updateschedule + "timeslice = '" + p_timeslice + "' , frequency = " + str(freq) + " , prev_schedule = '" + str(
                        prev_sche) + "' , next_schedule = '" + str(next_sche) + "' , updated_date = datetime('now', 'localtime') WHERE "
                    updateschedule = updateschedule + "comment='" + p_comment + "' AND isdeleted = 0;"
                    LOGGER.debug(updateschedule)

                    ml.db_execquery(updateschedule)
                    LOGGER.info('executed')
                    #######################Update Query#######################
                #*************************CRONTAB*************************#
                LOGGER.info('CRONTAB section end!')
                USER_CRON.write()  # Actual write to crontab
                LOGGER.info('CRONTAB write')
                #****$$****JSONDUMP****$$****#
                flag = '1'
                msg = 'Record updated successfully'
                dump = {'flag': flag, 'msg': msg}
                LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
                print json.dumps(dump)
                #****$$****JSONDUMP****$$****#
                LOGGER.info('JSON dumps')
            else:
                LOGGER.info('job not found')
    ##########################DISABLE JOB##########################

    ##########################FIND JOB##########################
    def find_job(p_comment):
        """Finds existing cron job"""
        LOGGER.info('FINDJOB')
        LOGGER.debug('p_comment : ' + p_comment)

        for job in USER_CRON.find_comment(p_comment):
            print job
    ##########################FIND JOB##########################

    ##########################REMOVE JOB##########################
    def remove_job(p_comment):
        """Removes existing cron job"""
        LOGGER.info('REMOVEJOB')
        LOGGER.debug('p_comment : ' + p_comment)

        LOGGER.info('checkjob')
        #######################Query to check whether a record exists in table#
        checkjob = "SELECT EXISTS (select * from schedular WHERE "
        checkjob = checkjob + "comment='" + p_comment + "' AND isdeleted = 0);"
        LOGGER.debug(checkjob)

        count = ml.db_fetchone(checkjob)
        LOGGER.info('executed')
        LOGGER.debug('count >> ' + str(count))
        #######################Query to check whether a record exists in table#

        if count == 1:
            LOGGER.info('REMOVING JOB...')
            LOGGER.info('CRONTAB section start')
            #*************************CRONTAB*************************#
            for job in USER_CRON.find_comment(p_comment):
                if "pi~@$^*" not in job.comment:  # To avoid pi Jobs
                    USER_CRON.remove(job)

                    LOGGER.info('removejob')
                    #######################Update Query#######################
                    removejob = "update schedular set "
                    removejob = removejob + \
                        "isdeleted = 1,updated_date = datetime('now', 'localtime') WHERE "
                    removejob = removejob + "comment='" + p_comment + "';"
                    LOGGER.debug(removejob)

                    ml.db_execquery(removejob)
                    LOGGER.info('executed')
                    #######################Update Query#######################

            #*************************CRONTAB*************************#
            LOGGER.info('CRONTAB section end!')
            USER_CRON.write()  # Actual write to crontab
            LOGGER.info('CRONTAB write')
            #****$$****JSONDUMP****$$****#
            flag = '1'
            msg = 'Record deleted successfully'
            dump = {'flag': flag, 'msg': msg}
            LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
            print json.dumps(dump)
            #****$$****JSONDUMP****$$****#
            LOGGER.info('JSON dumps')
        else:
            LOGGER.info('job not found')
    ##########################REMOVE JOB##########################

    ##########################UPDATE JOBS##########################
    def update_jobs():
        """Updates all existing cron jobs"""
        LOGGER.info('UPDATEJOBS')

        LOGGER.info('UPDATING SCHEDULE FOR ALL JOBS...')
        LOGGER.info('CRONTAB section start')
        #*************************CRONTAB*************************#
        for job in USER_CRON:
            comment = job.comment
            LOGGER.debug('comment : ' + comment)

            schedule = job.schedule(date_from=datetime.now())
            prev_sche = schedule.get_prev()
            next_sche = schedule.get_next()

            computeddetails = ' Prev Schedule:' + \
                str(prev_sche) + ' Next Schedule:' + str(next_sche)
            LOGGER.debug('computed details >> ' + computeddetails)

            LOGGER.info('updateschedule')
            #######################Update Query#######################
            updateschedule = "update schedular set "
            updateschedule = updateschedule + "prev_schedule = '" + \
                str(prev_sche) + "',next_schedule  = '" + \
                str(next_sche) + "' WHERE "
            updateschedule = updateschedule + "comment='" + \
                comment + "' AND isactive = 1 AND isdeleted = 0;"
            LOGGER.debug(updateschedule)

            ml.db_execquery(updateschedule)
            LOGGER.info('executed')
            #######################Update Query#######################
        #*************************CRONTAB*************************#
        LOGGER.info('CRONTAB section end!')
        #****$$****JSONDUMP****$$****#
        flag = '1'
        msg = 'All Records updated successfully'
        dump = {'flag': flag, 'msg': msg}
        LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
        print json.dumps(dump)
        #****$$****JSONDUMP****$$****#
        LOGGER.info('JSON dumps')
    ##########################UPDATE JOBS##########################

    ##########################PRINT ALL JOBS##########################
    def print_all_jobs():
        """Prints all existing cron job"""
        LOGGER.info('PRINT ALL JOBS')
        #*************************CRONTAB*************************#
        for job in USER_CRON:
            print job
        #*************************CRONTAB*************************#
    ##########################PRINT ALL JOBS##########################

    ##########################REMOVE ALL JOBS##########################
    def remove_all_jobs():
        """Removes all existing cron jobs"""
        LOGGER.info('REMOVEALLJOBS')

        LOGGER.info('REMOVING ALL JOBS...')
        LOGGER.info('CRONTAB section start')
        #*************************CRONTAB*************************#
        for job in USER_CRON:
            if "pi~@$^*" not in job.comment:
                USER_CRON.remove(job)
        #*************************CRONTAB*************************#
        LOGGER.info('CRONTAB section end!')

        LOGGER.info('removealljob')
        #######################Update Query#######################
        removealljob = "update schedular set "
        removealljob = removealljob + \
            "isdeleted = 1,updated_date = datetime('now', 'localtime');"
        LOGGER.debug(removealljob)

        ml.db_execquery(removealljob)
        LOGGER.info('executed')
        #######################Update Query#######################

        USER_CRON.write()  # Actual write to crontab
        LOGGER.info('CRONTAB write')
        #****$$****JSONDUMP****$$****#
        flag = '1'
        msg = 'All Records deleted successfully'
        dump = {'flag': flag, 'msg': msg}
        LOGGER.debug('dump >> flag:' + flag + ',msg:' + msg)
        print json.dumps(dump)
        #****$$****JSONDUMP****$$****#
        LOGGER.info('JSON dumps')
    ##########################REMOVE ALL JOBS##########################

   #-------------------------------------------------------START-------------------------------------------------------------#
    USER_CRON = CronTab(user=True)  # current user crontab
    LOGGER.warning('schedular has started with config. >> CronTab(user=True)')

    PARAM = "{:s}".format(sys.argv[1])  # fetch PARAM

    # Extraction of Details from PARAM
    ARR_PARAM = PARAM.split(',')
    P_CASE = ARR_PARAM[0]
    # Extraction of Details from PARAM

    LOGGER.debug('P_CASE : ' + P_CASE)

    if P_CASE == "1":
        COMMENT = ARR_PARAM[1]
        TIMESLICE = ARR_PARAM[2]
        COMMAND = ARR_PARAM[3]
        DEVICESTATE = ARR_PARAM[4]
        insert_job(COMMENT, TIMESLICE, COMMAND, DEVICESTATE)
        # UPDATEJOBS()#UpdateJobs after insert
    elif P_CASE == "2":
        COMMENT = ARR_PARAM[1]
        TIMESLICE = ARR_PARAM[2]
        enable_job(COMMENT, TIMESLICE)
        # UPDATEJOBS()#UpdateJobs after enable
    elif P_CASE == "3":
        COMMENT = ARR_PARAM[1]
        TIMESLICE = ARR_PARAM[2]
        disable_job(COMMENT, TIMESLICE)
        # UPDATEJOBS()#UpdateJobs after disable
    elif P_CASE == "4":
        COMMENT = ARR_PARAM[1]
        find_job(COMMENT)
    elif P_CASE == "5":
        COMMENT = ARR_PARAM[1]
        remove_job(COMMENT)
        # UPDATEJOBS()#UpdateJobs after remove
    elif P_CASE == "6":
        update_jobs()
    elif P_CASE == "7":
        print_all_jobs()
    elif P_CASE == "8":
        remove_all_jobs()

    LOGGER.warning('schedular has stopped <<')
   #-------------------------------------------------------START-------------------------------------------------------------#
except:
    LOGGER.exception("got error")
    LOGGER.critical('schedular has stopped unexpectedly!!! <<')
    raise
