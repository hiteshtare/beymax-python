#!/usr/bin/env python

import os , sys

import ConfigParser
import sqlite3
import logging
import logging.handlers
import rrdtool
from rrdtool import update as rrd_update

configname='/var/www/python_config.ini' #config path
dbname='/var/www/db/mydata.db' #db path
rddpath='/var/www/rdd/' #rdd path
logpath ='/var/www/logs/' #log path '/var/www/logs/debug.log'

def set_exit_handler(func):
    if os.name == "nt":
        try:
            import win32api
            win32api.SetConsoleCtrlHandler(func, True)
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
    else:
        import signal
        signal.signal(signal.SIGTERM, func)

def get_datetime():
    localtime   = time.localtime()
    timeString  = time.strftime("%d/%m/%Y %H:%M:%S", localtime)
    return timeString

def read_config():
    config = ConfigParser.ConfigParser()
    config.read(configname)
    return config

def init_logging(name,logfile):    
    logger = logging.getLogger(name)    
    logger.setLevel(logging.DEBUG)

    logname = logpath + logfile + '.log'
    # Add the log message handler to the logger
    rfh = logging.handlers.RotatingFileHandler(logname, mode='a', maxBytes=1*1024*1024, backupCount=5, encoding=None, delay=0) #1MB each * 5 = 5MB in total
    rfh.setLevel(logging.DEBUG)    
		
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
		
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s | %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    ch.setFormatter(formatter)
    rfh.setFormatter(formatter)   
		
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(rfh)
    return logger


def db_execquery(query): #execute sql query
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute(query)
    conn.commit()
    conn.close()
	
def db_fetchone(query): #execute and return first object 
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute(query)
    count = curs.fetchone()[0] #assigning value to count
    conn.close()
    return count


def db_fetchall(query): #execute and return first object 
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()   
    curs.execute(query)
    cursor = curs.fetchall()
    conn.close()
    return cursor
	 
def check_int(p_user_id,p_room_no,p_d_type,p_no,p_status_code): #check whether each string is of type integer   
    try: 
        int(p_user_id)
        int(p_room_no)
        int(p_d_type)
        int(p_no)
        int(p_status_code)
        return True
    except ValueError:
        return False				

def create_rdd(name,config):
    rrdtool.create(rddpath + name,config)

def update_rdd(name,param):
    rrd_update(rddpath + name, param);

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_filesize(path,name):
    fileinfo = os.stat(path + name)
    filesize = fileinfo.st_size
    filesize = sizeof_fmt(fileinfo.st_size)
    return filesize


def get_dirsize(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    total_size = sizeof_fmt(total_size)        
    return total_size

