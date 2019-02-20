#!/usr/bin/env python2
# -*- coding: utf-8 -*-  

# setting up libraries used in the program
from __future__ import print_function
from dronekit import connect
import exceptions
import socket
import time
import sys
import os

# clear screen
os.system("clear")

try:

    # print out the instruction
    print ("Take RC car's controller raw reading.")

    # connect to pixhawk
    print ("\nWith baudrate = %d." % 57600)
    print ("Connect to serial port = %s." % "/dev/ttyS0")
    vehicle = connect("/dev/ttyS0", heartbeat_timeout = 30, baud = 57600)

    # print out instruction
    print ("\nTo end the program press [CTRL] + [c].\n")
    
    # take 3 [s] break
    time.sleep(3)

    # infinity loop
    while True:

        # reading rc input from channel 1 to channel 12
        a = vehicle.channels['1']
        b = vehicle.channels['2']
        c = vehicle.channels['3']
        d = vehicle.channels['4']
        e = vehicle.channels['5']
        f = vehicle.channels['6']
        g = vehicle.channels['7']
        h = vehicle.channels['8']

        # print out the input
        print ("CH1 %s, CH2 %s, CH3 %s, CH4 %s, CH5 %s, CH6 %s, CH7 %s, CH8 %s." 
        % (a, b, c, d, e, f, g, h))
        
        # sleep for 3 second
        time.sleep(3)

except KeyboardInterrupt:

    print ("\n\n[CTRL] + [c] detected.")

finally:

    print ("Program is terminated.")
    vehicle.close()
    quit()
