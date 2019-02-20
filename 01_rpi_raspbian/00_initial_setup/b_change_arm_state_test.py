#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# setting up modules used in the program
from dronekit import connect
import exceptions
import socket
import time
import os

# clear screen
os.system("clear")

# arming and disarming test
try:

    # print out the instruction
    print ("Testing the arming and disarming sequence.")

    # connect to pixhawk
    print ("\nWith baudrate = %d." % 57600)
    print ("Connect to serial port = %s." % "/dev/ttyS0")
    vehicle = connect("/dev/ttyS0", heartbeat_timeout = 30, baud = 57600)

    # change state to disarmed for 5 seconds
    print ("\nPixhawk will enter disarmed state for 5 seconds.")
    vehicle.armed = False
    print ("State: %s" % vehicle.armed)
    time.sleep(5)

    # change state to armed for 5 seconds
    print ("\nPixhawk will enter armed state for 5 seconds.")
    vehicle.armed = True
    print ("State: %s" % vehicle.armed)
    time.sleep(5)

    # change state to disarmed for 5 seconds
    print ("\nPixhawk will enter disarmed state for 5 seconds.")
    vehicle.armed = False
    print ("State: %s" % vehicle.armed)
    time.sleep(5)

# test failed
except:

    print ("\nPixhawk failed the arming and disarming test.\n")

# test passed
else:

    print ("\nPixhawk passed the arming and disarming test.\n")
    # close dronekit
    vehicle.close()