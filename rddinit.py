#!/usr/bin/python
import sys
import traceback

import rrdtool

import mylib as ml #user-defined

try:

    name = 'rdd'
    logfile = 'rdd'
    logger = ml.init_logging(name,logfile)
    logger.warning('rddinit has started >> ')

    logger.info('New rdd')
        
    rddname = 'humidity.rrd'
    logger.debug('name : ' + rddname)

    
##    rddconfig = ["--start", "N","--step", "300", 
##   "DS:a:GAUGE:600:0:50",
##   "DS:b:GAUGE:600:0:80",
##   "RRA:AVERAGE:0.5:1:288",
##   "RRA:AVERAGE:0.5:3:672",
##   "RRA:AVERAGE:0.5:12:8880"]
    
    rddconfig = ["--start", "N","--step", "3600", 
   "DS:a:GAUGE:7200:0:80",
   "DS:b:GAUGE:7200:0:80",
   "RRA:AVERAGE:0.5:1:3200",
   "RRA:AVERAGE:0.5:3:8000",
   "RRA:AVERAGE:0.5:12:10656"]

    logger.debug('config : ')
                 
    for item in rddconfig:
        logger.debug(item)

    ml.create_rdd(rddname,rddconfig)
    logger.info('rdd created')
                 
    logger.warning('rddinit has stopped <<')
except:
    logger.exception("got error")
    logger.critical('rddinit has stopped unexpectedly!!! <<')
    raise
