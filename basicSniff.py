
import time
import pigpio
import vw
import sys
import traceback

import os

import mylib as ml #user-defined

import myrddlib as mrddl #user-defined

try:
  
  name = 'RFSniffer'
  logger = ml.init_logging(name)

  RX=20
  TX=19

  BPS=2000

  pi = pigpio.pi() # Connect to local Pi.

  rx = vw.rx(pi, RX, BPS) # Specify Pi, rx GPIO, and baud.
  tx = vw.tx(pi, TX, BPS) # Specify Pi, tx GPIO, and baud.
  
  n = 3
  msg = 0

  start = time.time()

  config = 'RX:' + str(RX) + ' BPS:' + str(BPS)
  logger.warning('RFSniffer has started with config. >> ' + config)

  caltemp = "";#testing

  while (time.time()-start) > 0:

    while not tx.ready():
      time.sleep(0.02)
	
      time.sleep(0.1)

    while not tx.ready():
      time.sleep(0.02)

      time.sleep(0.1)

    while rx.ready():
        rvalue = ("".join(chr (c) for c in rx.get()))
        rvalue_len = len(rvalue)
            
        print(rvalue)
  
  rx.cancel() # Cancel Virtual Wire receiver.

  pi.stop() # Disconnect from local Pi.

  logger.warning('RFSniffer has stopped <<')
  
except:
    logger.exception("got error")
    logger.critical('RFSniffer has stopped unexpectedly!!! <<')
