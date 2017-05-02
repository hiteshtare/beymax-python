#!/usr/bin/env python
"""python exec begin"""

import ConfigParser
import logging
import logging.handlers
import os
import sqlite3
import sys

import rrdtool
from rrdtool import update as rrd_update

CONFIG_NAME = '/var/www/python_config.ini'  # config path
DB_NAME = '/var/www/db/mydata.db'  # db path
RDD_PATH = '/var/www/rdd/'  # rdd path
LOG_PATH = '/var/www/logs/'  # log path '/var/www/logs/debug.log'


def set_exit_handler(func):
    """Sets exit handler for my library"""
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
    """Fetchs machine's local time"""
    localtime = time.localtime()
    time_string = time.strftime("%d/%m/%Y %H:%M:%S", localtime)
    return time_string


def read_config():
    """Parses user-defined config"""
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_NAME)
    return config


def init_logging(name, logfile):
    """Initialises logger with custom settings"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    logname = LOG_PATH + logfile + '.log'
    # Add the log message handler to the logger
    rfh = logging.handlers.RotatingFileHandler(
        logname, mode='a', maxBytes=1 * 1024 * 1024, backupCount=5, encoding=None, delay=0)  # 1MB each * 5 = 5MB in total
    rfh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    cons_hand = logging.StreamHandler()
    cons_hand.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s | %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    cons_hand.setFormatter(formatter)
    rfh.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(cons_hand)
    logger.addHandler(rfh)
    return logger


def db_execquery(query):
    """Executes a sql query"""
    conn = sqlite3.connect(DB_NAME)
    curs = conn.cursor()
    curs.execute(query)
    conn.commit()
    conn.close()


def db_fetchone(query):
    """Executes a sql query and returns first object"""
    conn = sqlite3.connect(DB_NAME)
    curs = conn.cursor()
    curs.execute(query)
    count = curs.fetchone()[0]  # assigning value to count
    conn.close()
    return count


def db_fetchall(query):
    """Executes a sql query and returns all objects"""
    conn = sqlite3.connect(DB_NAME)
    curs = conn.cursor()
    curs.execute(query)
    cursor = curs.fetchall()
    conn.close()
    return cursor


def check_int(p_user_id, p_room_no, p_d_type, p_no, p_status_code):
    """Checks whether each string is of type integer"""
    try:
        int(p_user_id)
        int(p_room_no)
        int(p_d_type)
        int(p_no)
        int(p_status_code)
        return True
    except ValueError:
        return False


def create_rdd(name, config):
    """Creates rdd chart"""
    rrdtool.create(RDD_PATH + name, config)


def update_rdd(name, param):
    """Updates rdd chart"""
    rrd_update(RDD_PATH + name, param)


def zipdir(path, ziph):
    """Creates a zip file"""
    for root, files in os.walk(path):
        for file_present in files:
            ziph.write(os.path.join(root, file_present))


def sizeof_fmt(num, suffix='B'):
    """Calculates the size of a zip file"""
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_filesize(path, name):
    """Gets size of a file"""
    fileinfo = os.stat(path + name)
    filesize = fileinfo.st_size
    filesize = sizeof_fmt(fileinfo.st_size)
    return filesize


def get_dirsize(start_path):
    """Gets size of a directory"""
    total_size = 0
    for dirpath, filenames in os.walk(start_path):
        for file_n in filenames:
            file_present = os.path.join(dirpath, file_n)
            total_size += os.path.getsize(file_present)
    total_size = sizeof_fmt(total_size)
    return total_size
