#!/usr/bin/env python2
# -*- coding: utf-8 -*-  

# setting up modules used in the program
from __future__ import print_function
import a_prefix_variable as apv
from dronekit import connect
from socket import socket
import threading
import picamera
import socket
import struct
import time
import sys
import os
import io

# threading 1; create a class for camera (video) client
class VideoStreamClient(threading.Thread):

    # initialize threading 1, client socket address and port
    def __init__(self, host1, port1):

        # client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        # client condition
        self.connected = False 

        # while client haven't connected to server
        while not (self.connected):

            try:

                # reconnecting to server
                self.client_socket.connect((host1, port1))
                self.connection = self.client_socket.makefile('wb')
                self.connected = True

            except Exception as e:

                # if failed try again
                pass
        
        # execute client sending
        self.sending()

    # when connection with server is established
    def sending(self):

        try:
                    
            # initialize raspberry pi camera module parameter
            with picamera.PiCamera() as camera:

                # video resolution
                camera.resolution = (apv.x, apv.y)
                # frames/second     
                camera.framerate = apv.fps
                # give 2 [s] for camera module to initilize
                time.sleep(2)                       
                start = time.time()
                stream = io.BytesIO()

                # send jpeg format video stream
                for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):

                    # get start time
                    start = time.time()

                    # if kill switch for threading 1 is activated
                    if (LatchingSwitch.tr_alive != True):

                        # break from for loop
                        break

                    # pack the jpeg data into struct
                    self.connection.write(struct.pack('<L', stream.tell()))
                    self.connection.flush()
                    stream.seek(0)
                    self.connection.write(stream.read())

                    # after 10 minutes
                    if (time.time() - start > 600):
                        
                        # break from for loop
                        break

                    # seek and truncate stream
                    stream.seek(0)
                    stream.truncate()

                    # print time taken to prepare 1 image
                    print ("Frame take %.3f [s] to complete" % (time.time() - start))

            # write the terminating 0-length to the connection to let the video server know we're done
            self.connection.write(struct.pack('<L', 0))

        except:

            # do nothing
            pass

        else:
            
            # quit the raspberry pi camera module client threading nicely
            self.connection.close()
            self.client_socket.close()

# threading 2; create a class for rangefinder client
class RangeFinderClient(threading.Thread):

    # initialize threading 2, client socket address and port
    def __init__(self, host2, port2):

        # client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        # client condition
        self.connected = False 

        # while client haven't connected to server
        while not (self.connected):

            try:

                # reconnecting to server
                self.client_socket.connect((host2, port2))
                self.connection = self.client_socket.makefile('wb')
                self.connected = True

            # if failed
            except Exception as e:

                # if kill switch is activated
                if (LatchingSwitch.tr_alive != True):

                    # stop trying
                    self.connected = True

                # if kill switch is not activated
                else:

                    # try again
                    pass
        
        # execute client sending
        self.sending()

    # when connection with server is established
    def sending(self):

        try:
            
            # while loop
            while True:

                # if kill switch for threading 2 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get distance reading from rangefinder
                measured_distance = int(ConnectPixhawk.serial.rangefinder.distance * 100)

                # if distance reading is more than apv.truncate [cm]
                if (measured_distance > apv.truncate):

                    # truncate distance reading
                    measured_distance = apv.truncate

                # print distance reading
                print ("Distance in front is %d [cm]" % measured_distance)
                # send distance reading to lidar rangefinder server
                self.client_socket.send(str(measured_distance).encode())
                # sleep for 0.1 [s]
                time.sleep(0.1)

        except:

            # do nothing
            pass

        else:
            
            # quit lidar rangefinder client nicely
            self.client_socket.close()

# threading 3; create a class for futaba controller (driving) server
class ControllerDriveServer(threading.Thread):

    # initialize threading 3, server socket address and port
    def __init__(self, host3, port3):

        # futaba controller channel 1
        self.left = apv.left
        self.right = apv.right
        self.center = apv.center
        # futaba controller channel 3
        self.backward = apv.backward
        self.forward = apv.forward
        self.stop = apv.stop
        # server socket
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host3, port3))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # arming the rover
            ConnectPixhawk.serial.armed = True
            # override channel 1 and channel 3 to default state
            ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}

            # while loop
            while True:

                # if kill switch for threading 3 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # receive input from futaba controller client
                user_input = int(self.connection.recv(1024).decode())

                # if user_input = 0
                if (user_input == 0):

                    # brake and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
                    print ("Move ■")

                # user_input = 1
                elif (user_input == 1):

                    # forward and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.forward, '1':self.center}
                    print ("Move ↑")

                # user_input = 2
                elif (user_input == 2):

                    # forward and the steering is turning right
                    ConnectPixhawk.serial.channels.overrides = {'3':self.forward, '1':self.right}
                    print ("Move →")

                # user_input = 3
                elif (user_input == 3):

                    # forward and the steering is turning left
                    ConnectPixhawk.serial.channels.overrides = {'3':self.forward, '1':self.left}
                    print ("Move ←")

                # user_input = 4
                elif (user_input == 4):

                    # backward and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.backward, '1':self.center}
                    print ("Move ↓")

        except:

            # reset channels 1 and 3 position
            ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
            # reset channels 1 and 3 override
            ConnectPixhawk.serial.channels.overrides = {'3':None, '1':None}
            # disarming the rover
            ConnectPixhawk.serial.armed = False

        else:

            # reset channels 1 and 3 position
            ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
            # reset channels 1 and 3 override
            ConnectPixhawk.serial.channels.overrides = {'3':None, '1':None}
            # disarming the rover
            ConnectPixhawk.serial.armed = False
            # quit futaba controller server nicely
            self.connection.close()
            self.server_socket.close()

# threading 4; create a class for futaba controller (training) server
class ControllerTrainServer(threading.Thread):

    # initialize server socket address and port
    def __init__(self, host4, port4):

        # futaba controller channel 1
        self.left = apv.left
        self.right = apv.right
        self.center = apv.center
        # futaba controller channel 3
        self.backward = apv.mbackward
        self.forward = apv.mforward
        self.stop = apv.stop
        # server socket
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host4, port4))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # arming the rover
            ConnectPixhawk.serial.armed = True
            # override channel 1 and channel 3 to default state
            ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}

            # while loop
            while True:

                # if kill switch for threading 2 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # reading from rangefinder
                measured_distance = int(ConnectPixhawk.serial.rangefinder.distance * 100)

                # if rangefinder reading is more than apv.truncate [cm]
                if (measured_distance > apv.truncate):

                    # truncate rangefinder reading to apv.truncate [cm]
                    measured_distance = apv.truncate
                
                # print out measured distance
                print ("Rangefinder Distance: %d [cm]" % measured_distance)

                # receive input from futaba controller client
                user_input = int(self.connection.recv(1024).decode())

                # if user_input = 0
                if (user_input == 0):

                    # brake and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
                    print ("Move ■")
                    # take 0.3 [s] rest
                    time.sleep(0.3)
                    # brake and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
                    print ("Move ■")

                # else if user_input = 1
                elif (user_input == 1):

                    # forward and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.forward, '1':self.center}
                    print ("Save ↑")
                    # take 0.3 [s] rest
                    time.sleep(0.3)
                    # stop and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
                    print ("Move ■")

                # else if user_input = 2
                elif (user_input == 2):

                    # forward and the steering is turning right
                    ConnectPixhawk.serial.channels.overrides = {'3':self.forward, '1':self.right}
                    print ("Save →")
                    # take 0.3 [s] rest
                    time.sleep(0.3)
                    # stop and the steering is turning right
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.right}
                    print ("Move ■")

                # else if user_input = 3
                elif (user_input == 3):

                    # forward and the steering is turning left
                    ConnectPixhawk.serial.channels.overrides = {'3':self.forward, '1':self.left}
                    print ("Save ←")
                    # take 0.3 [s] rest
                    time.sleep(0.3)
                    # stop and the steering is turning left
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.left}
                    print ("Move ■")

                # else if user_input = 4
                elif (user_input == 4):

                    # backward and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.backward, '1':self.center}
                    print ("Save ↓")
                    # take 0.3 [s] rest
                    time.sleep(0.3)
                    # backward and the steering is centered
                    ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
                    print ("Move ■")

        except:

            # reset channels 1 and 3 position
            ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
            # reset channels 1 and 3 override
            ConnectPixhawk.serial.channels.overrides = {'3':None, '1':None}
            # disarming the rover
            ConnectPixhawk.serial.armed = False

        else:

            # reset channels 1 and 3 position
            ConnectPixhawk.serial.channels.overrides = {'3':self.stop, '1':self.center}
            # reset channels 1 and 3 override
            ConnectPixhawk.serial.channels.overrides = {'3':None, '1':None}
            # disarming the rover
            ConnectPixhawk.serial.armed = False
            # quit futaba controller server nicely
            self.connection.close()
            self.server_socket.close()

# step 1; system compatibility check
class CompatibilityCheck(object):

    # check os compatibility
    if (os.name == 'nt'):

        print ("\nThis codes only compatible with Linux OS!\n")
        exit()

    # check python environment compatibility
    if (sys.version_info[0] > 2):

        print ("\nThis codes only compatible with Python 2 environment!\n")
        exit()

# step 2; connect raspberry pi with pixhawk
class ConnectPixhawk(object):

    # suppressing messages or errors from dronekit
    def suppress_print(x):

        # do nothing
        pass

    # establishing connection between raspberry pi and pixhawk
    serial = connect(apv.connection, heartbeat_timeout = apv.timeout, baud = apv.baud, status_printer = suppress_print)

# step 3; initialize latching switch to communicate with threading 1, 2, 3, 4
class LatchingSwitch(object):

    # initialize switches variables
    tr_alive = None

    # initialize switches value
    def __init__(self):

        # assign switches value to true
        LatchingSwitch.tr_alive = True

    # change switches value
    def killswitch(self):

        # assign switches value to false
        LatchingSwitch.tr_alive = False

# step 4; control latching switch condition and manage individual threading 1, 2, 3, 4
class ThreadingManager(object):

    try:

        # initialize pick
        pick = None
        # LatchingSwitch class is now switch
        switch = LatchingSwitch()

        # while loop
        while True:

            # clear the screen
            os.system("clear")
            # print out info for user
            print ("This Python program will act as an interface for APM: Rover to allow user or artificial")
            print ("intelligence to control it remotely via Transmission Control Protocol from PC.")
            print ("\nPick the task you want to run. To stop at any time given press [CTRL] + [c].")
            print ("[1] Live streaming test.")
            print ("[2] Steer data collection.")
            print ("[3] Autonomous self-driving.")
            # get user input
            pick = raw_input ("\nYour pick: ")

            # if pick is 1
            if (pick == b'1'):

                # print out info for user
                print ("\nThis Python program will run server and clients as a threadings on Raspberry")
                print ("Pi to live streaming test data from video feeds, rangefinder reading and")
                print ("user control input to be accepted and viewed live on user PC side.")
                print ("To stop at any time given press [CTRL] + [c].")
                # get user input
                raw_input ("\nTo start press [Enter].")
                # set classes as threadings
                tr1 = threading.Thread(target = VideoStreamClient, args = (apv.pc, apv.video))
                tr2 = threading.Thread(target = RangeFinderClient, args = (apv.pc, apv.rangefinder))
                tr3 = threading.Thread(target = ControllerDriveServer, args = (apv.rpi, apv.controller))
                # set threadings as daemons
                tr1.daemon = True
                tr2.daemon = True
                tr3.daemon = True
                # start the threading
                tr1.start()
                tr2.start()
                tr3.start()
                # print out info for user
                print ("\nThreading start, waiting connection from PC side.\n")
                # break from the while loop
                break

            # else if pick is 2
            elif (pick == b'2'):

                # print out info for user
                print ("\nThis Python program will live streaming data from video feeds and user control input")
                print ("from Raspberry pi to be recorded on PC side. Recorded data will be use to")
                print ("train artificial intelligence on how to steer the car in real time.")
                print ("\nTo stop at any time given press [CTRL] + [c].")
                # get user input
                raw_input ("\nTo start press [Enter].")
                # set classes as threadings
                tr1 = threading.Thread(target = VideoStreamClient, args = (apv.pc, apv.video))
                tr4 = threading.Thread(target = ControllerTrainServer, args = (apv.rpi, apv.controller))
                # set threadings as daemons
                tr1.daemon = True
                tr4.daemon = True
                # start the threading
                tr1.start()
                tr4.start()
                # print out info for user
                print ("\nThreading start, waiting connection from PC side.\n")
                # break from the while loop
                break

            # else if pick is 3
            elif (pick == b'3'):

                # print out info for user
                print ("\nThis Python program will live streaming data from video feeds, user control input")
                print ("and rangefinder from Raspberry Pi so that the artificial intelligence")
                print ("on PC side can make decision on how to steer the rover.")
                print ("To stop at any time given press [CTRL] + [c].")
                # get user input
                raw_input ("\nTo start press [Enter].")
                # set classes as threadings
                tr1 = threading.Thread(target = VideoStreamClient, args = (apv.pc, apv.video))
                tr2 = threading.Thread(target = RangeFinderClient, args = (apv.pc, apv.rangefinder))
                tr3 = threading.Thread(target = ControllerDriveServer, args = (apv.rpi, apv.controller))
                # set threadings as daemons
                tr1.daemon = True
                tr2.daemon = True
                tr3.daemon = True
                # start the threading
                tr1.start()
                tr2.start()
                tr3.start()
                # print out info for user
                print ("\nThreading start, waiting connection from PC side.\n")
                # break from the while loop
                break

        # take 5 seconds break
        time.sleep(5)

        # if pick is 1 or 3 (both run the same processes)
        if ((pick == b'1') or (pick == b'3')):

            # check threading 1, 2, 3 to see if it is alive or not
            while True:

                # if threading1 is dead
                if ((tr1.is_alive() != True) and (tr2.is_alive() == True) and (tr3.is_alive() == True)):

                    # print the message
                    print ("\nVideo client threading ended prematurely.\n")
                    # raise exception
                    raise Exception

                # else if threading2 is dead
                elif ((tr1.is_alive() == True) and (tr2.is_alive() != True) and (tr3.is_alive() == True)):

                    # print the message
                    print ("\nRangefinder client threading ended prematurely.\n")
                    # raise exception
                    raise Exception

                # else if threading3 is dead
                elif ((tr1.is_alive() == True) and (tr2.is_alive() == True) and (tr3.is_alive() != True)):

                    # print the message
                    print ("\nFutaba controller server threading ended prematurely.\n")
                    # raise exception
                    raise Exception

                # # if more than 1 threading is dead
                elif ((tr1.is_alive() != True) or (tr2.is_alive() != True) or (tr3.is_alive() != True)):

                    # print the message
                    print ("\nTCP connection was terminated on PC side.\n")
                    # raise exception
                    raise Exception

                # stop before looping again in 3 [s]
                time.sleep(3)

        # else if pick is 2
        elif (pick == b'2'):

            # check threading 1, 4 to see if it is alive or not
            while True:

                # if threading1 is dead
                if ((tr1.is_alive() != True) and (tr4.is_alive() == True)):

                    # print the message
                    print ("\nVideo client threading ended prematurely.\n")
                    # raise exception
                    raise Exception

                # else if threading4 is dead
                elif ((tr1.is_alive() == True) and (tr4.is_alive() != True)):

                    # print the message
                    print ("\nFutaba controller server threading ended prematurely.\n")
                    # raise exception
                    raise Exception

                # else if all threading is dead
                elif ((tr1.is_alive() != True) and (tr4.is_alive() != True)):

                    # print the message
                    print ("\nTCP connection was terminated on PC side.\n")
                    # raise exception
                    raise Exception

                # stop before looping again in 3 [s]
                time.sleep(3)

    except KeyboardInterrupt:

        # when [CTRL] + [c] is pressed print the message
        print ("\n[CTRL] + [c] is pressed.\n")

    except:

        # when exception is raised print the message
        print ("\nException raised.\n")

    finally:

        # turn on the kill switch
        switch.killswitch()
        # give time for threading to close
        time.sleep(3)
        # close connection between raspberry pi and pixhawk
        ConnectPixhawk.serial.close()
        # print out message
        print ("\nProgram ended.\n")

# initiator
if __name__ == '__main__':

    # step 1; run compatibility check sequence
    CompatibilityCheck()
    # step 2; connecting raspberry pi with pixhawk
    ConnectPixhawk()
    # step 3; initialize latching switch
    LatchingSwitch()
    # step 4; initialize threading
    ThreadingManager()