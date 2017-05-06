#!/usr/bin/env python
"""This file deals with sending code through RF"""

import sys
import time
import traceback

import mylib as ml  # user-defined
import pigpio
import vw

CONFIG = ml.read_config()

NAME = 'codesend'
LOGFILE = 'debug'
LOGGER = ml.init_logging(NAME, LOGFILE)

try:

    TX = int(CONFIG.get("vw", "TX_Code"))
    BPS = int(CONFIG.get("vw", "BPS"))

    PI = pigpio.pi()  # Connect to local Pi.

    TX = vw.tx(PI, TX, BPS)  # Specify Pi, TX GPIO, and baud.

    CONFIG = ' TX:' + str(TX) + ' BPS:' + str(BPS)
    LOGGER.warning('codesend has started with CONFIG. >> ' + CONFIG)

    while TX.ready():

        # TX.put("{:s}".format(sys.argv[1]))

        R_VALUE = "{:s}".format(sys.argv[1])

        R_VALUE_LEN = len(R_VALUE)

        # print(R_VALUE)
        LOGGER.debug('R_VALUE : ' + R_VALUE + ' length : ' + str(R_VALUE_LEN))

        if R_VALUE_LEN == 10:  # Code recieved from web (Valid)

            # Extraction of Details from Code
            USER_ID = (R_VALUE[0:3])
            STR_ROOM_NO = (R_VALUE[3:5])
            ROOM_NO = str(int((R_VALUE[3:5])))
            D_TYPE = (R_VALUE[5:7])
            NO = (R_VALUE[7:8])
            STATUS_CODE = (R_VALUE[8:10])
            # Extraction of Details from Code

            DETAILS = 'USER_ID:' + USER_ID + ' ROOM_NO:' + ROOM_NO + \
                ' D_TYPE:' + D_TYPE + ' NO:' + NO + ' STATUS_CODE:' + STATUS_CODE
            LOGGER.debug('DETAILS >> ' + DETAILS)

            if STATUS_CODE != "99":  # To avoid code that is triggered by rpi

                LOGGER.info('DEVICE_CHECK')
                # Query to check whether a record exists i
                DEVICE_CHECK = "SELECT EXISTS (SELECT * FROM revoke WHERE "
                DEVICE_CHECK = DEVICE_CHECK + "deviceid=" + \
                    USER_ID + STR_ROOM_NO + D_TYPE + NO + " );"
                LOGGER.debug(DEVICE_CHECK)

                COUNT = ml.db_fetchone(DEVICE_CHECK)
                LOGGER.info('executed')
                LOGGER.debug('COUNT >> ' + str(COUNT))
                # Query to check whether a record exists i
                if COUNT == 1:
                    # Query to check whether a record exis
                    LOGGER.info('REVOKE_CHECK')
                    REVOKE_CHECK = "SELECT EXISTS (SELECT * FROM revoke WHERE "
                    REVOKE_CHECK = REVOKE_CHECK + "deviceid=" + USER_ID + \
                        STR_ROOM_NO + D_TYPE + NO + " AND ischeck=1 );"
                    LOGGER.debug(REVOKE_CHECK)

                    COUNT = ml.db_fetchone(REVOKE_CHECK)
                    LOGGER.info('executed')
                    LOGGER.debug('COUNT >> ' + str(COUNT))
                    # Query to check whether a record exis

                    if COUNT == 1:  # record already exists go with updation
                        LOGGER.info('true')
                    else:
                        LOGGER.info('false')
                        break

                TX.put("{:s}".format(sys.argv[1]))  # forward to RFSniffer
                LOGGER.info('CHECK_SQL')
                # Query to check whether a record exists i
                CHECK_SQL = "SELECT EXISTS (SELECT * FROM devicestat WHERE "
                CHECK_SQL = CHECK_SQL + "userid=" + USER_ID + " AND room=" + \
                    ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ");"
                LOGGER.debug(CHECK_SQL)

                COUNT = ml.db_fetchone(CHECK_SQL)
                LOGGER.info('executed')
                LOGGER.debug('COUNT >> ' + str(COUNT))

                # Query to check whether a record exists i

                if COUNT == 1:  # record already exists go with updation
                    LOGGER.info('UPDATE_SQL')

                    #######################Update Query#######################
                    UPDATE_SQL = "UPDATE devicestat SET "
                    UPDATE_SQL = UPDATE_SQL + "status =" + STATUS_CODE + \
                        " , updated_date = datetime('NOw', 'localtime') , ack = 0  WHERE "
                    UPDATE_SQL = UPDATE_SQL + "userid=" + USER_ID + " AND room=" + \
                        ROOM_NO + " AND type=" + D_TYPE + " AND NO=" + NO + ";"
                    LOGGER.debug(UPDATE_SQL)

                    ml.db_execquery(UPDATE_SQL)
                    LOGGER.info('executed')
                    #######################Update Query#######################

                else:  # record does NOt exists go with insertion
                    LOGGER.info('INSERT_SQL')

                    #######################Insert Query#######################
                    INSERT_SQL = "INSERT INTO devicestat (userid, room, type, NO, status,updated_date) VALUES ("
                    INSERT_SQL = INSERT_SQL + USER_ID + "," + ROOM_NO + "," + D_TYPE + \
                        "," + NO + "," + STATUS_CODE + \
                        ",datetime('NOw', 'localtime'));"
                    LOGGER.debug(INSERT_SQL)

                    ml.db_execquery(INSERT_SQL)
                    LOGGER.info('executed')
                    #######################Insert Query#######################
            else:
                LOGGER.info('trigger update from rpi')
                TX.put("{:s}".format(sys.argv[1]))  # forward to RFSniffer

        elif len(R_VALUE) == 11:  # Code is Recieved from rpi
            LOGGER.info('Recieved from RPI')
            TX.put("{:s}".format(sys.argv[1]))  # forward to RFSniffer
        else:  # Code is Invalid
            LOGGER.info('Invalid Code Length!')
            TX.put("{:s}".format(sys.argv[1]))  # forward to RFSniffer

    while not TX.ready():
        time.sleep(0.02)

    TX.cancel()  # Cancel Virtual Wire transmitter.

    PI.stop()

    LOGGER.warning('codesend has stopped <<')

except:
    LOGGER.exception("got error")
    LOGGER.critical('codesend has stopped unexpectedly!!! <<')
