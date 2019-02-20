#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# read distance measured from rangefinder attached to pixhawk

# setting up modules used in the program
from __future__ import print_function
from dronekit import connect
import exceptions
import socket
import time
import os

# clear screen
os.system("clear")

try:

    # print out the instruction
    print ("Take RC car's rangefinder distance reading.")

    # connect to pixhawk
    print ("\nWith baudrate = %d." % 57600)
    print ("Connect to serial port = %s." % "/dev/ttyS0")
    vehicle = connect("/dev/ttyS0", heartbeat_timeout = 30, baud = 57600)
    
    # print out instruction
    print ("\nTo end the program press [CTRL] + [c].\n")

    # take 3 [s] break
    time.sleep(3)

    # measure distance
    while True:

        # reading from rangefinder
        rangefinder_distance = vehicle.rangefinder.distance
        # print out the reading from rangefinder
        print ("Rangefinder Distance: %.2f [m]" % float(rangefinder_distance))
        # 1 sec delay
        time.sleep(1)

# when user press [CTRL] + [c]
except KeyboardInterrupt:

    print ("\n\n[CTRL] + [c] detected.")

finally:

    print ("Program is terminated.")
    # close dronekit
    vehicle.close()
