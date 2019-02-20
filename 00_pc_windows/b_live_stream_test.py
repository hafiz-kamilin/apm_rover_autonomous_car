#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules used in the program
import a_prefix_variable as apv
from pygame.locals import *
from socket import socket
import pygame.display
import numpy as np
import threading
import pygame
import socket
import time
import cv2
import sys
import os

# threading 1; create a class for raspberry pi camera module server
class VideoStreamServer(threading.Thread):

    # initialize threading 1, server socket address and port
    def __init__(self, host1, port1):

        # server socket and port
        self.server_socket = socket.socket()
        self.server_socket.bind((host1, port1))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # need bytes here
            stream_bytes = b' '
            # LatchingSwitch class is now switch
            switch = LatchingSwitch()
            
            # while loop
            while True:

                # if kill switch for threading 1 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get start time
                start = time.time()
                # find first and last byte of jpg stream
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                # if first and last byte is not -1
                if ((first != -1) and (last != -1)):

                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    # turn jpg data into something understandable to opencv and crop it
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    # print time taken to prepare 1 image
                    print ("Frame take %.3f [s] to complete" % (time.time() - start))
                    # display the data stream as video
                    cv2.imshow("To quit press [q].", image)

                    # to close opencv windows press [q]
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        
                        # turn on the kill switch 2
                        switch.killswitch2()
                        # break from while loop
                        break

        except:

            # do nothing
            pass

        else:

            # quit video server nicely
            self.connection.close()
            self.server_socket.close()

# threading 2; create a class for lidar rangefinder server
class RangeFinderServer(threading.Thread):
    
    # initialize threading 2, server socket address and port
    def __init__(self, host2, port2):

        # server socket and port
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host2, port2))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # while loop
            while True:

                # if kill switch for threading 2 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # receive the distance reading from the client
                distance = int(self.connection.recv(1024).decode())
                # print out the distance
                print ("Distance in front is %d [cm]" % distance)

        except:

            # do nothing
            pass

        else:

            # quit rangefinder server nicely
            self.connection.close()
            self.server_socket.close()

# threading 3; create a class for futaba controller client
class ControllerDriveClient(threading.Thread):

    # initialize threading 3, client socket address and port
    def __init__(self, host3, port3):

        # client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        # client condition
        self.connected = False
        # arrow_switch condition
        self.arrow_switch = None

        # while client haven't connected to server
        while not (self.connected):

            try:

                # reconnecting to server
                self.client_socket.connect((host3, port3))
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

        # open small pygame windows to take user input
        pygame.display.init()
        screen = pygame.display.set_mode((250,250))

        try:

            # initialize self.arrow_switch to 0
            self.arrow_switch = 0
            # LatchingSwitch class is now switch
            switch = LatchingSwitch()

            # while loop
            while self.connected:

                # if kill switch for threading 3 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get user input to control the rover
                for event in pygame.event.get():

                    # key break
                    if event.type == pygame.KEYUP:

                        self.arrow_switch = 0

                    # when the key was pressed down
                    elif event.type == KEYDOWN:
                        
                        # register the pressed down key
                        user_input = pygame.key.get_pressed()

                        # if it is ↑
                        if user_input[pygame.K_UP]:

                            self.arrow_switch = 1

                        # else if it is →
                        elif user_input[pygame.K_RIGHT]:

                            self.arrow_switch = 2                    

                        # else if it is ←
                        elif user_input[pygame.K_LEFT]:

                            self.arrow_switch = 3

                        # else if it is ↓
                        elif user_input[pygame.K_DOWN]:

                            self.arrow_switch = 4
                        
                        # else if it [q]
                        elif user_input[pygame.K_q]:

                            # turn on the kill switch 2
                            switch.killswitch2()
                            self.connected = False

                # send command to rover to brake
                if (self.arrow_switch == 0):
                    
                    self.client_socket.send('0'.encode())
                    print ("Steer ■")

                # send command to rover to move forward
                if (self.arrow_switch == 1):
                    
                    self.client_socket.send('1'.encode())
                    print ("Steer ↑")

                # send command to rover to turn right
                elif (self.arrow_switch == 2):
                    
                    self.client_socket.send('2'.encode())
                    print ("Steer →")

                # send command to rover to turn left
                elif (self.arrow_switch == 3):
                    
                    self.client_socket.send('3'.encode())
                    print ("Steer ←")

                # send command to rover to move backward
                elif (self.arrow_switch == 4):
                    
                    self.client_socket.send('4'.encode())
                    print ("Steer ↓")

                time.sleep(0.1)

        except:

            # do nothing
            pass

        else:
            
            # quit futaba controller client nicely
            self.client_socket.close()

# step 1; system compatibility check
class CompatibilityCheck(object):

    # check os compatibility
    if (os.name != 'nt'):

        print ("\nThis codes only compatible with Windows OS!\n")
        exit()

    # check python environment compatibility
    if (sys.version_info[0] < 3):

        print ("\nThis codes only compatible with Python 3 environment!\n")
        exit()

# step 2; initialize latching switch to communicate with threading 1, 2, 3
class LatchingSwitch(object):

    # initialize switches variables
    tr_alive = None

    # initialize switches value
    def __init__(self):

        # assign switches value to true
        LatchingSwitch.tr_alive = True

    # change switches value
    def killswitch1(self):

        # assign switches value to false
        LatchingSwitch.tr_alive = False

    # change switches value
    def killswitch2(self):

        # assign switches value to None
        LatchingSwitch.tr_alive = None

# step 3; control latching switch condition and manage individual threading 1, 2, 3
class ThreadingManager(object):

    # LatchingSwitch class is now switch
    switch = LatchingSwitch()

    try:

        # clear the screen
        os.system("cls")
        # print out info for user
        print ("This Python program will run server and clients as a threadings on user PC to streaming")
        print ("test data from video feeds, rangefinder reading and user control input")
        print ("to be accepted and viewed live on user PC side.")
        print ("\nTo stop before TCP connection is established press [CTRL] + [c] on console, to stop")
        print ("after TCP connection is established press [q] on Pygame or OpenCV windows.")
        # get user input
        input ("\nTo start press [Enter].")
        # set classes as threadings
        tr1 = threading.Thread(target = VideoStreamServer, args = (apv.pc, apv.video))
        tr2 = threading.Thread(target = RangeFinderServer, args = (apv.pc, apv.rangefinder))
        tr3 = threading.Thread(target = ControllerDriveClient, args = (apv.rpi, apv.controller))
        # set threadings as daemon
        tr1.daemon = True
        tr2.daemon = True
        tr3.daemon = True
        # set classes as threadings
        tr1.start()
        tr2.start()
        tr3.start()
        # print out info for user
        print ("\nThreading start, waiting connection from RPi side.\n")

        # check threading 1, 2, 3 to see if it is alive or not
        while True:

            # if program ended nicely
            if (LatchingSwitch.tr_alive == None):

                # break from while loop
                break

            # if threading1 is dead
            if ((tr1.is_alive() != True) and (tr2.is_alive() == True) and (tr3.is_alive() == True)):

                # print the message
                print ("\nVideoStreamServer threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading2 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() != True) and (tr3.is_alive() == True)):

                # print the message
                print ("\nRangeFinderServer threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading3 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() == True) and (tr3.is_alive() != True)):

                # print the message
                print ("\nControllerDriveClient threading ended prematurely.\n")
                # raise exception
                raise Exception

            # if more than 1 threading is dead
            elif ((tr1.is_alive() != True) or (tr2.is_alive() != True) or (tr3.is_alive() != True)):

                # print the message
                print ("\nTCP connection was terminated on Raspberry Pi side.\n")
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

        # turn on the kill switch 1
        switch.killswitch1()
        # give time for threading to close
        time.sleep(3)
        # print out message
        print ("\nProgram ended.\n")

# initiator
if __name__ == '__main__':

    # step 1; run compatibility check sequence
    CompatibilityCheck()
    # step 2; initialize latching switch
    LatchingSwitch()
    # step 3; initialize threading
    ThreadingManager()