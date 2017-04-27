import time
import sys
import os

timeout = time.time() + 1*1   # 1 minutes from now

#rvalue = sys.argv[1]
#settime = sys.argv[2]
#settime = int(settime)
    
while True:
    
    if time.time() > timeout:
        #timeout == time.time() + 30*1
        print 'timmer reset'
        print timeout
        break

print '1 minute elapsed!!!'

