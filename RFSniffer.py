#!/usr/bin/env python
"""This file deals with mail management"""

import os
import subprocess
import sys
import time
import traceback

import mylib as ml  # user-defined
import pigpio
import vw

CONFIG = ml.read_config()

NAME = 'RFSniffer'
LOG_FILE = 'debug'
LOGGER = ml.init_logging(NAME, LOG_FILE)

NAME = 'rdd'
LOG_FILE = 'rdd'
LOGGER1 = ml.init_logging(NAME, LOG_FILE)

NAME = 'MotionDetect'
LOG_FILE = 'motion'
LOGGER2 = ml.init_logging(NAME, LOG_FILE)

try:

    RX = int(CONFIG.get("vw", "RX"))
    TX = int(CONFIG.get("vw", "TX_RF"))
    BPS = int(CONFIG.get("vw", "BPS"))

    PI = pigpio.pi()  # Connect to local Pi.

    RX = vw.rx(PI, RX, BPS)  # Specify Pi, rx GPIO, and baud.
    TX = vw.tx(PI, TX, BPS)  # Specify Pi, tx GPIO, and baud.

    NUM = 3
    MSG = 0

    START = time.time()

    CONFIG = ' TX:' + str(TX) + ' RX:' + str(RX) + ' BPS:' + str(BPS)
    LOGGER.warning('RFSniffer has started with CONFIG. >> ' + CONFIG)

    LOGGER1.warning('RFSniffer has started >> ')

    CAL_TEMP = ""  # testing

    while (time.time() - START) > 0:

        while not TX.ready():
            time.sleep(0.02)

            time.sleep(0.1)

        while not TX.ready():
            time.sleep(0.02)

            time.sleep(0.1)

        while RX.ready():
            R_VALUE = ("".join(chr(c) for c in RX.get()))
            R_VALUE_LEN = len(R_VALUE)

            print R_VALUE
            LOGGER.debug('R_VALUE : ' + R_VALUE +
                         ' length : ' + str(R_VALUE_LEN))

            if R_VALUE_LEN == 11:  # Code with ACK recieved from rpi (Valid)

                # Extraction of Details from R_VALUE
                USER_ID = (R_VALUE[0:3])
                ROOM_NO = str(int((R_VALUE[3:5])))
                D_TYPE = (R_VALUE[5:7])
                NO = (R_VALUE[7:8])
                STATUS_CODE = (R_VALUE[8:10])
                # Extraction of Details from R_VALUE

                DETAILS = 'USER_ID:' + USER_ID + ' ROOM_NO:' + ROOM_NO + \
                    ' D_TYPE:' + D_TYPE + ' NO:' + NO + ' STATUS_CODE:' + STATUS_CODE
                LOGGER.debug('DETAILS >> ' + DETAILS)

                CODE_VALID = False
                LOGGER.info('code validity check >>')
                CODE_VALID = True if ml.check_int(
                    USER_ID, ROOM_NO, D_TYPE, NO, STATUS_CODE) else False

                if CODE_VALID == True:
                    # Query to check whether a give table
                    #-----------------------------To Check Table Exists new logic--------------------------------------#
                    LOGGER.debug('TABLE_SQL')
                    TABLE_SQL = "SELECT COUNT(NAME) FROM sqlite_master WHERE type='table' AND "
                    TABLE_SQL = TABLE_SQL + "NAME='room" + ROOM_NO + "_log';"
                    LOGGER.debug(TABLE_SQL)

                    COUNT = ml.db_fetchone(TABLE_SQL)
                    LOGGER.info('executed')
                    LOGGER.debug('COUNT >> ' + str(COUNT))

                    if COUNT == 0:  # table does not exists go with creation
                        LOGGER.info('new log table creation : NEW_TABLE_SQL')
                        #######################new Table Creation##############
                        NEW_TABLE_SQL = "CREATE TABLE room" + ROOM_NO + "_log"
                        NEW_TABLE_SQL = NEW_TABLE_SQL + \
                            " (userid int, room int, type int, NO int, status int, inserted_date datetime);"
                        LOGGER.debug(NEW_TABLE_SQL)

                        ml.db_execquery(NEW_TABLE_SQL)
                        LOGGER.info('executed')
                        #######################new Table Creation##############

                        #######################Insert entry in table Rooms#####
                        LOGGER.info('new entry in rooms : INSERT_ENTRY')

                        INSERT_ENTRY = "insert into rooms (room ,NAME ,alias ,isactive ,islog ,inserted_date ,updated_date) values ("
                        INSERT_ENTRY = INSERT_ENTRY + ROOM_NO + ",'room" + ROOM_NO + "','room" + \
                            ROOM_NO + \
                            "',1,1,datetime('now', 'localtime'),datetime('now', 'localtime'));"
                        LOGGER.debug(INSERT_ENTRY)

                        ml.db_execquery(INSERT_ENTRY)
                        LOGGER.info('executed')
                #######################Insert entry in table Rooms#############

                #------------------------------------------------------------------------#
                # Query to check whether a give table exis
                    if D_TYPE == "07":  # Motion
                        LOGGER2.info('*--------*Motion Detection*--------*')
                        print '*--------*Motion Detection*--------*'
                        LOGGER2.info('CHECK_SQL')
                        # Query to check whether a record
                        CHECK_SQL = "SELECT EXISTS (select * from motion WHERE "
                        CHECK_SQL = CHECK_SQL + "userid=" + USER_ID + " AND room=" + \
                            ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ");"
                        LOGGER2.debug(CHECK_SQL)

                        COUNT = ml.db_fetchone(CHECK_SQL)
                        LOGGER2.info('executed')
                        LOGGER2.debug('COUNT >> ' + str(COUNT))
                        # Query to check whether a record

                        if COUNT == 1:  # record already exists go with updation

                            if STATUS_CODE == "10":
                                LOGGER2.info('DETECTION_OFF')
                                DETECTION_OFF = "update motion set "
                                DETECTION_OFF = DETECTION_OFF + "status =" + STATUS_CODE + \
                                    " , updated_date = datetime('now', 'localtime') WHERE "
                                DETECTION_OFF = DETECTION_OFF + "userid=" + USER_ID + " AND room=" + \
                                    ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                                LOGGER2.debug(DETECTION_OFF)

                                ml.db_execquery(DETECTION_OFF)
                                LOGGER2.info('executed')
                            elif STATUS_CODE == "11":
                                LOGGER2.info('detectionon')
                                DETECTION_OFF = "update motion set "
                                DETECTION_OFF = DETECTION_OFF + "status =" + STATUS_CODE + \
                                    " , updated_date = datetime('now', 'localtime') WHERE "
                                DETECTION_OFF = DETECTION_OFF + "userid=" + USER_ID + " AND room=" + \
                                    ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                                LOGGER2.debug(DETECTION_OFF)

                                ml.db_execquery(DETECTION_OFF)
                                LOGGER2.info('executed')
                            elif STATUS_CODE == "13":
                                LOGGER2.info('NO_MORE_DETECTION')
                                NO_MORE_DETECTION = "update motion set "
                                NO_MORE_DETECTION = NO_MORE_DETECTION + "status =" + STATUS_CODE + \
                                    " , updated_date = datetime('now', 'localtime') WHERE "
                                NO_MORE_DETECTION = NO_MORE_DETECTION + "userid=" + USER_ID + " AND room=" + \
                                    ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                                LOGGER2.debug(NO_MORE_DETECTION)

                                ml.db_execquery(NO_MORE_DETECTION)
                                LOGGER2.info('executed')
                            else:
                                print 'else Motion STATUS_CODE : ' + STATUS_CODE
                                LOGGER2.info('CHECK_RUNNING')

                                # Query to check whether a
                                CHECK_RUNNING = "SELECT EXISTS (select * from motion WHERE "
                                CHECK_RUNNING = CHECK_RUNNING + "userid=" + USER_ID + " AND room=" + ROOM_NO + \
                                    " AND type=" + D_TYPE + " AND NO=" + NO + "  AND isrunning = 1);"
                                LOGGER2.debug(CHECK_RUNNING)

                                COUNT = ml.db_fetchone(CHECK_RUNNING)
                                LOGGER2.info('executed')
                                LOGGER2.debug('COUNT >> ' + str(COUNT))

                                if COUNT == 1:  # record already is already in running state
                                    LOGGER2.warning(
                                        'ALREADY RUNNING : python motiondetect.py 60 ')
                                    print(
                                        'ALREADY RUNNING : python motiondetect.py 60 ')

                                    print 'UPDATE_RUNNING'
                                    LOGGER2.info('UPDATE_RUNNING')
                                    UPDATE_RUNNING = "update motion set "
                                    UPDATE_RUNNING = UPDATE_RUNNING + \
                                        "status = 12 , updated_date = datetime('now', 'localtime') WHERE "
                                    UPDATE_RUNNING = UPDATE_RUNNING + "userid=" + USER_ID + " AND room=" + \
                                        ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                                    LOGGER2.debug(UPDATE_RUNNING)

                                    ml.db_execquery(UPDATE_RUNNING)
                                    LOGGER2.info('executed')
                                else:
                                    print 'INSERT_RUNNING'
                                    LOGGER2.info('INSERT_RUNNING')
                                    #######################Update Query########
                                    INSERT_RUNNING = "update motion set "
                                    INSERT_RUNNING = INSERT_RUNNING + "status =" + STATUS_CODE + \
                                        " , isrunning = 1, start_date = datetime('now', 'localtime'), updated_date = datetime('now', 'localtime') WHERE "
                                    INSERT_RUNNING = INSERT_RUNNING + "userid=" + USER_ID + " AND room=" + \
                                        ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                                    LOGGER2.debug(INSERT_RUNNING)

                                    ml.db_execquery(INSERT_RUNNING)
                                    LOGGER2.info('executed')
                                    #os.popen('sudo python codesend.py 1010101111')
                                    LOGGER.warning(
                                        'python motiondetect.py ' + R_VALUE + ' 60')
                                    RESTART_PROCESS = subprocess.Popen(
                                        'python motiondetect.py ' + R_VALUE + ' 60', shell=True)
                                    #######################Update Query########

                        else:  # record does not exists go with insertion
                            LOGGER.info('INSERT_SQL')
                            #######################Insert Query################
                            INSERT_SQL = "insert into motion (userid, room, type, NO, status, inserted_date, updated_date) values ("
                            INSERT_SQL = INSERT_SQL + USER_ID + "," + ROOM_NO + "," + D_TYPE + "," + NO + "," + \
                                STATUS_CODE + \
                                ",datetime('now', 'localtime'),datetime('now', 'localtime'));"
                            LOGGER.debug(INSERT_SQL)

                            ml.db_execquery(INSERT_SQL)
                            LOGGER.info('executed')
                            #######################Insert Query################
                    elif D_TYPE == "13":  # Water
                        LOGGER.info('*--------*Water Level Reading*--------*')
                    elif D_TYPE == "14":  # Temperature
                      #######################Insert Temperature################
                        LOGGER.info('*--------*Temperature Reading*--------*')

                        CAL_TEMP = STATUS_CODE + "." + NO

                        LOGGER.info('CHECK_ROOM_TEMP')
                        # Query to check whether a record
                        CHECK_ROOM_TEMP = "SELECT EXISTS (select * from temps WHERE roomno=" + \
                            ROOM_NO + " );"
                        LOGGER.debug(CHECK_ROOM_TEMP)

                        COUNT = ml.db_fetchone(CHECK_ROOM_TEMP)
                        LOGGER.info('executed')
                        LOGGER.debug('COUNT >> ' + str(COUNT))

                        if COUNT == 1:  # record already exists go with updation
                            LOGGER.info('UPDATE_ROOM_TEMP')

                            UPDATE_ROOM_TEMP = "update temps set "
                            UPDATE_ROOM_TEMP = UPDATE_ROOM_TEMP + "temp =" + CAL_TEMP + \
                                " , timestamp = datetime('now', 'localtime') WHERE "
                            UPDATE_ROOM_TEMP = UPDATE_ROOM_TEMP + " roomno=" + ROOM_NO + " ;"
                            LOGGER.debug(UPDATE_ROOM_TEMP)

                            ml.db_execquery(UPDATE_ROOM_TEMP)
                            LOGGER.info('executed')
                        else:
                            LOGGER.info('INSERT_ROOM_TEMP')

                            INSERT_ROOM_TEMP = "insert into temps (roomno, temp,timestamp) values ("
                            INSERT_ROOM_TEMP = INSERT_ROOM_TEMP + ROOM_NO + "," + \
                                CAL_TEMP + ",datetime('now', 'localtime'));"
                            LOGGER.debug(INSERT_ROOM_TEMP)

                            ml.db_execquery(INSERT_ROOM_TEMP)
                            LOGGER.info('executed')
                      #######################Insert Temperature################
                    elif D_TYPE == "15":  # Humidity
                        #######################Insert Humidity#################
                        LOGGER.info('*--------*Humidity Reading*--------*')

                        CAL_HUMI = STATUS_CODE + "." + NO

                        LOGGER.info('CHECK_ROOM_HUMI')
                        # Query to check whether a record
                        CHECK_ROOM_HUMI = "SELECT EXISTS (select * from humis WHERE roomno=" + \
                            ROOM_NO + " );"
                        LOGGER.debug(CHECK_ROOM_HUMI)

                        COUNT = ml.db_fetchone(CHECK_ROOM_HUMI)
                        LOGGER.info('executed')
                        LOGGER.debug('COUNT >> ' + str(COUNT))

                        if COUNT == 1:  # record already exists go with updation
                            LOGGER.info('UPDATE_ROOM_HUMI')

                            UPDATE_ROOM_HUMI = "update humis set "
                            UPDATE_ROOM_HUMI = UPDATE_ROOM_HUMI + "humi =" + CAL_HUMI + \
                                " , timestamp = datetime('now', 'localtime') WHERE "
                            UPDATE_ROOM_HUMI = UPDATE_ROOM_HUMI + " roomno=" + ROOM_NO + " ;"
                            LOGGER.debug(UPDATE_ROOM_HUMI)

                            ml.db_execquery(UPDATE_ROOM_HUMI)
                            LOGGER.info('executed')
                        else:
                            LOGGER.info('INSERT_ROOM_HUMI')

                            INSERT_ROOM_HUMI = "insert into humis (roomno, humi,timestamp) values ("
                            INSERT_ROOM_HUMI = INSERT_ROOM_HUMI + ROOM_NO + "," + \
                                CAL_HUMI + ",datetime('now', 'localtime'));"
                            LOGGER.debug(INSERT_ROOM_HUMI)

                            ml.db_execquery(INSERT_ROOM_HUMI)
                            LOGGER.info('executed')

                        LOGGER1.info('RDDTool section START')
                        LOGGER1.info('Building PARAM : ')  # testing
                        NAME = 'temperature_perhour.rrd'
                        PARAM = 'N:' + CAL_TEMP + ':' + CAL_HUMI  # testing
                        LOGGER1.debug(PARAM)  # testing
                        LOGGER1.info('update_rdd >> NAME ' + NAME)
                        ml.update_rdd('temperature_perhour.rrd',
                                      PARAM)  # testing
                        LOGGER1.info('executed')

                        LOGGER1.warning(
                            '#####################TEMPEARTURE#####################')

                        FETCH_TEMP1 = "select temp from temps WHERE roomno=1;"
                        LOGGER.debug(FETCH_TEMP1)

                        TEMP1 = ml.db_fetchone(FETCH_TEMP1)
                        LOGGER.info('executed')
                        LOGGER.debug('TEMP1 >> ' + str(TEMP1))

                        FETCH_TEMP2 = "select temp from temps WHERE roomno=2;"
                        LOGGER.debug(FETCH_TEMP2)

                        TEMP2 = ml.db_fetchone(FETCH_TEMP2)
                        LOGGER.info('executed')
                        LOGGER.debug('TEMP2 >> ' + str(TEMP2))

                        LOGGER1.info('Building PARAM : ')
                        NAME = 'temperature.rrd'
                        PARAM = 'N:' + str(TEMP1) + ':' + str(TEMP2)
                        LOGGER1.debug(PARAM)
                        LOGGER1.info('update_rdd >> NAME ' + NAME)
                        ml.update_rdd(NAME, PARAM)
                        LOGGER1.info('executed')
                        LOGGER1.warning(
                            '#####################TEMPEARTURE#####################')

                        LOGGER1.warning(
                            '#####################HUMIDITY#####################')

                        FETCH_HUMI1 = "select humi from humis WHERE roomno=1;"
                        LOGGER.debug(FETCH_HUMI1)

                        HUMI1 = ml.db_fetchone(FETCH_HUMI1)
                        LOGGER.info('executed')
                        LOGGER.debug('HUMI1 >> ' + str(HUMI1))

                        FETCH_HUMI2 = "select humi from humis WHERE roomno=2;"
                        LOGGER.debug(FETCH_HUMI2)

                        HUMI2 = ml.db_fetchone(FETCH_HUMI2)
                        LOGGER.info('executed')
                        LOGGER.debug('HUMI2 >> ' + str(HUMI2))

                        LOGGER1.info('Building PARAM : ')
                        NAME = 'humidity.rrd'
                        PARAM = 'N:' + str(HUMI1) + ':' + str(HUMI2)
                        LOGGER1.debug(PARAM)
                        LOGGER1.info('update_rdd >> NAME ' + NAME)
                        ml.update_rdd(NAME, PARAM)
                        LOGGER1.info('executed')
                        LOGGER1.warning(
                            '#####################HUMIDITY#####################')

                        LOGGER1.info('RDDTool section end!')
                        #######################Insert Humidity#################
                    else:  # DeviceStat
                        LOGGER.info('CHECK_SQL')
                        # Query to check whether a record
                        CHECK_SQL = "SELECT EXISTS (select * from devicestat WHERE "
                        CHECK_SQL = CHECK_SQL + "userid=" + USER_ID + " AND room=" + \
                            ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ");"
                        LOGGER.debug(CHECK_SQL)

                        COUNT = ml.db_fetchone(CHECK_SQL)
                        LOGGER.info('executed')
                        LOGGER.debug('COUNT >> ' + str(COUNT))
                        # Query to check whether a record

                        if COUNT == 1:  # record already exists go with updation
                            LOGGER.info('UPDATE_SQL')
                            #######################Update Query################
                            UPDATE_SQL = "update devicestat set "
                            UPDATE_SQL = UPDATE_SQL + "status =" + STATUS_CODE + \
                                " , updated_date = datetime('now', 'localtime') , ack = 1 WHERE "
                            UPDATE_SQL = UPDATE_SQL + "userid=" + USER_ID + " AND room=" + \
                                ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                            LOGGER.debug(UPDATE_SQL)

                            ml.db_execquery(UPDATE_SQL)
                            LOGGER.info('executed')
                            #######################Update Query################

                            LOGGER.info('INSERT_LOG')
                            #######################Insert Log##################
                            INSERT_LOG = "insert into room" + ROOM_NO + \
                                "_log (userid, room, type, NO, status,inserted_date) values ("
                            INSERT_LOG = INSERT_LOG + USER_ID + "," + ROOM_NO + "," + D_TYPE + \
                                "," + NO + "," + STATUS_CODE + \
                                ",datetime('now', 'localtime'));"

                            ml.db_execquery(INSERT_LOG)
                            LOGGER.info('executed')
                            #######################Insert Log##################
                        else:  # record does not exists go with insertion
                            LOGGER.info(
                                'trigger update from device : INSERT_SQL')
                            #######################Insert Query################
                            INSERT_SQL = "insert into devicestat (userid, room, type, NO, status,updated_date) values ("
                            INSERT_SQL = INSERT_SQL + USER_ID + "," + ROOM_NO + "," + D_TYPE + \
                                "," + NO + "," + STATUS_CODE + \
                                ",datetime('now', 'localtime'));"
                            LOGGER.debug(INSERT_SQL)

                            ml.db_execquery(INSERT_SQL)
                            LOGGER.info('executed')
                            #######################Insert Query################

                            LOGGER.info('INSERT_LOG')
                            #######################Insert Log##################
                            INSERT_LOG = "insert into room" + ROOM_NO + \
                                "_log (userid, room, type, NO, status,inserted_date) values ("
                            INSERT_LOG = INSERT_LOG + USER_ID + "," + ROOM_NO + "," + D_TYPE + \
                                "," + NO + "," + STATUS_CODE + \
                                ",datetime('now', 'localtime'));"

                            ml.db_execquery(INSERT_LOG)
                            LOGGER.info('executed')
                            #######################Insert Log##################
                else:
                    LOGGER.info('Invalid Code')

            elif len(R_VALUE) == 10:  # Code is Recieved from Web
                LOGGER.info('Recieved from WEB PAGE')
            else:  # Code is Invalid
                LOGGER.info('Invalid Code Length')

            # conn.close() #conn close

    RX.cancel()  # Cancel Virtual Wire receiver.

    PI.stop()  # Disconnect from local Pi.

    #LOGGER.warning('RFSniffer has stopped <<')
    #LOGGER1.warning('RFSniffer has stopped <<')


except:
    LOGGER.exception("got error")
    LOGGER.critical('RFSniffer has stopped unexpectedly!!! <<')
