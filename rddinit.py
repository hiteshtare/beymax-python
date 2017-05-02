#!/usr/bin/python
"""This file deals with rdd charts"""

import sys
import traceback

import mylib as ml  # user-defined
import rrdtool

try:

    NAME = 'rdd'
    LOG_FILE = 'rdd'
    LOGGER = ml.init_logging(NAME, LOG_FILE)
    LOGGER.warning('rddinit has started >> ')

    LOGGER.info('New rdd')

    RDD_NAME = 'humidity.rrd'
    LOGGER.debug('NAME : ' + RDD_NAME)


# RDD_CONFIG = ["--start", "N","--step", "300",
# "DS:a:GAUGE:600:0:50",
# "DS:b:GAUGE:600:0:80",
# "RRA:AVERAGE:0.5:1:288",
# "RRA:AVERAGE:0.5:3:672",
# "RRA:AVERAGE:0.5:12:8880"]

    RDD_CONFIG = ["--start", "N", "--step", "3600", "DS:a:GAUGE:7200:0:80", "DS:b:GAUGE:7200:0:80",
                  "RRA:AVERAGE:0.5:1:3200",
                  "RRA:AVERAGE:0.5:3:8000",
                  "RRA:AVERAGE:0.5:12:10656"]

    LOGGER.debug('config : ')

    for item in RDD_CONFIG:
        LOGGER.debug(item)

    ml.create_rdd(RDD_NAME, RDD_CONFIG)
    LOGGER.info('rdd created')

    LOGGER.warning('rddinit has stopped <<')
except:
    LOGGER.exception("got error")
    LOGGER.critical('rddinit has stopped unexpectedly!!! <<')
    raise
