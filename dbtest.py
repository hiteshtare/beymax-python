#!/usr/bin/env python

import time
import pigpio
import vw
import sys
import traceback

import os
import subprocess
import mylib as ml #user-defined

try:

  fetch_humi1 = "select humi from humis WHERE roomno=1;";                         
     
  humi1 = ml.db_fetchone(fetch_humi1)
  print "humi1 :" + str(humi1)

  
  fetch_humi2 = "select humi from humis WHERE roomno=2;";                         
     
  humi2 = ml.db_fetchone(fetch_humi2)
  print "humi2 :" + str(humi2)

  
  fetch_temp1 = "select temp from temps WHERE roomno=1;";                         
     
  temp1 = ml.db_fetchone(fetch_temp1)
  print "temp1 :" + str(temp1)

  
  fetch_temp2 = "select temp from temps WHERE roomno=2;";                         
     
  temp2 = ml.db_fetchone(fetch_temp2)
  print "temp2 :" + str(temp2)

except:
  raise
