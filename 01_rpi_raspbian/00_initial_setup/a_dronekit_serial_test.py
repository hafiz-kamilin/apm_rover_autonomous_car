#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# setting up modules used in the program
import exceptions
import dronekit
import socket
import os

# clear screen
os.system("clear")

try:

    # print out the instruction
    print ("Testing the serial connection between Pixhawk and Raspberry Pi.")

    # connect to pixhawk
    print ("\nWith baudrate = %d." % 57600)
    print ("Connect to serial port = %s." % "/dev/ttyS0")
    dronekit.connect("/dev/ttyS0", heartbeat_timeout = 30, baud = 57600)

# bad tty connection error
except exceptions.OSError as e:

    print ("\nNo serial exists!\n")

# api error
except dronekit.APIException:

    print ("\nTimeout!\n")

# other error
except:

    print ("\nSome unidentified error!\n")

# succesful connection
else:
    
    print ("\nDroneKit manage to connect with Pixhawk!\n")