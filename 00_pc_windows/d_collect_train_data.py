#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules used in the program
import a_prefix_variable as apv
from datetime import datetime
from pygame.locals import *
from numpy import load
import numpy as np
import threading
import pygame
import socket
import shutil
import glob
import time
import cv2
import sys
import os

# threading 1; create a class for steer data collect class
class SteerDataCollect(threading.Thread):

    # initialize steer_command as shared variable
    steer_command = None

    # initialize threading 1, server socket address, port and matrix
    def __init__(self, host1, port1):

        # assign value to steer_command
        SteerDataCollect.steer_command = 5
        # server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host1, port1))
        self.server_socket.listen(0)
        # accept a single connection ('rb' is 'read binary')
        self.connection = self.server_socket.accept()[0].makefile('rb')
        # establish a condition that rpi is streaming video right now
        self.send_inst = True
        # creates a 3x3 matrix filled with zero
        self.k = np.zeros((3, 3), 'float')
        
        # put 1's along the diagonal, upper left to bottom right:
        for i in range(3):

            # array([[ 1.,  0.,  0.],
            #        [ 0.,  1.,  0.],
            #        [ 0.,  0.,  1.])
            self.k[i, i] = 1

        # create temp_label filled with 0 float
        self.temp_label = np.zeros((1, 3), 'float')
        # execute collecting images and input
        self.collect_images()

    # when connection from rpi camera is established
    def collect_images(self):

        # open small pygame windows to take user input
        pygame.init()
        pygame.display.set_mode((250, 250))
        # frame counters
        frame = 0
        saved_frame = 0
        total_frame = 0
        # click counts
        clicks_forward = 0
        clicks_forward_left = 0
        clicks_forward_right = 0

        # if the apv.folder01 path doesn't exist create empty path
        if not os.path.exists(apv.folder00 + "/" + apv.folder01):

            os.makedirs(apv.folder00 + "/" + apv.folder01)

        # if the apv.folder02 path doesn't exist create empty path
        if not os.path.exists(apv.folder00 + "/" + apv.folder02):

            os.makedirs(apv.folder00 + "/" + apv.folder02)

        # if apv.tempfolder00 already exist delete the path
        if os.path.exists(apv.folder00 + "/" + apv.tempfolder00):
        
            shutil.rmtree(apv.folder00 + "/" + apv.tempfolder00)

        # if apv.tempfolder01 already exist delete the path
        if os.path.exists(apv.folder00 + "/" + apv.tempfolder01):
        
            shutil.rmtree(apv.folder00 + "/" + apv.tempfolder01)

        # create new apv.tempfolder00 path
        os.makedirs(apv.folder00 + "/" + apv.tempfolder00)
        # create new apv.tempfolder01 path
        os.makedirs(apv.folder00 + "/" + apv.tempfolder01)
        # label_array is ([0., 0., 0.,])
        label_array = np.zeros((1, 3), 'float')
        # LatchingSwitch class is now switch
        switch = LatchingSwitch()

        try:

            # need bytes here
            stream_bytes = b' '
            # LatchingSwitch class is now switch
            switch = LatchingSwitch()

            # while loop
            while self.send_inst:

                # if kill switch for threading 1 is activated
                if (LatchingSwitch.tr_alive != True):

                    # raise exception
                    raise Exception

                # find first and last byte of jpg stream
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                # if first and last byte is not -1
                if first != -1 and last != -1:

                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    # 'image0' original image in color cropped to x = 320 and y = 120 for livestreaming
                    image0 = cv2.imdecode(np.fromstring(jpg, dtype = np.uint8), cv2.IMREAD_COLOR)[120:240, :]
                    # 'image1' original image in color, full frame for training
                    image1 = cv2.imdecode(np.fromstring(jpg, dtype = np.uint8), cv2.IMREAD_COLOR)
                    # apply gaussian blurring to reduces noise
                    image2 = cv2.GaussianBlur(image1, (3, 3), 0)[120:240, :]
                    # compute the median of the single channel pixel intensities
                    median = np.median(image2)
                    # lower parameter for edge canny detection
                    lower = int(max(100, (1.0 - apv.sigma) * median))
                    # higher parameter for edge canny detection
                    upper = int(min(300, (1.0 + apv.sigma) * median))                    
                    # 'image2' filtered image1 using canny edge detection for storing
                    image2 = cv2.Canny(image2, lower, upper)
                    # overlay click counts on image0
                    clicks_total = clicks_forward + clicks_forward_left + clicks_forward_right
                    cv2.putText(image0, "FW: {}, LT: {}, RT: {}, TOTAL: {}".format(clicks_forward, clicks_forward_left, clicks_forward_right, clicks_total), (10, 30), cv2.FONT_HERSHEY_DUPLEX, .45, (0, 0, 255), 1)
                    # display feeds on host (pc)
                    cv2.imshow("Video Feed.", image0)
                    # calculate frame and total frame
                    frame += 1
                    total_frame += 1

                    # get user input to control the rover
                    for event in pygame.event.get():

                        # when the key was pressed down
                        if event.type == KEYDOWN:
                            
                            # register the pressed down key
                            key_input = pygame.key.get_pressed()
                            # get the current time
                            timestr = datetime.now().strftime("%Y%m%d%H%M%S%f")

                            # brake; images and input won't be saved
                            if key_input[pygame.K_b]:
                                
                                # change steer_command value to brake
                                SteerDataCollect.steer_command = 0
                                # rest for 0.3 second
                                time.sleep(0.3)
                                # reset steer_command back to default value
                                SteerDataCollect.steer_command = 5

                            # forward; save the images and input
                            elif key_input[pygame.K_UP]:

                                # save processed image1 as original image (color)
                                cv2.imwrite(apv.folder00 + "/" + apv.tempfolder00 + '/' + '{}.jpg'.format(timestr), image1)
                                # save processed image1 as filtered image (canny)
                                cv2.imwrite(apv.folder00 + "/" + apv.tempfolder01 + '/' + '{}.jpg'.format(timestr), image2)
                                # (↑) self.k[1] = [ 0.,  1.,  0.]
                                label_array = np.vstack((label_array, self.k[1]))
                                # change steer_command value to move forward
                                SteerDataCollect.steer_command = 1
                                # increment the counters
                                clicks_forward += 1
                                saved_frame += 1
                                # rest for 0.3 second
                                time.sleep(0.3)
                                # reset steer_command back to default value
                                SteerDataCollect.steer_command = 5
                                # print out to the user
                                print ("Saved ↑")

                            # forward right; save the images and input
                            elif key_input[pygame.K_RIGHT]:

                                # save processed image1 as original image (color)
                                cv2.imwrite(apv.folder00 + "/" + apv.tempfolder00 + '/' + '{}.jpg'.format(timestr), image1)
                                # save processed image1 as filtered image (canny)
                                cv2.imwrite(apv.folder00 + "/" + apv.tempfolder01 + '/' + '{}.jpg'.format(timestr), image2)
                                # (→) self.k[2] = [ 0.,  0.,  1.]
                                label_array = np.vstack((label_array, self.k[2]))
                                # change steer_command value to move forward & turn right
                                SteerDataCollect.steer_command = 2
                                # increment the counters
                                clicks_forward_right += 1
                                saved_frame += 1
                                # rest for 0.3 second
                                time.sleep(0.3)
                                # reset steer_command back to default value
                                SteerDataCollect.steer_command = 5
                                # print out to the user
                                print ("Saved →")

                            # forward left; save the images and input
                            elif key_input[pygame.K_LEFT]:

                                # save processed image1 as original image (color)
                                cv2.imwrite(apv.folder00 + "/" + apv.tempfolder00 + '/' + '{}.jpg'.format(timestr), image1)
                                # save processed image1 as filtered image (canny)
                                cv2.imwrite(apv.folder00 + "/" + apv.tempfolder01 + '/' + '{}.jpg'.format(timestr), image2)
                                # (←) self.k[0] = [ 1.,  0.,  0.]
                                label_array = np.vstack((label_array, self.k[0]))
                                # change steer_command value to move forward & turn left
                                SteerDataCollect.steer_command = 3
                                # increment the counters
                                clicks_forward_left += 1
                                saved_frame += 1
                                # rest for 0.3 second
                                time.sleep(0.3)
                                # reset steer_command back to default value
                                SteerDataCollect.steer_command = 5
                                # print out to the user
                                print ("Saved ←")

                            # reverse; images and input won't be saved
                            elif key_input[pygame.K_DOWN]:
                                
                                # change steer_command value to reverse
                                SteerDataCollect.steer_command = 4
                                # rest for 0.3 second
                                time.sleep(0.3)
                                # reset steer_command back to default value
                                SteerDataCollect.steer_command = 5

                            # to end the program press [q] key on pygame window
                            elif key_input[pygame.K_q]:

                                # break from while loop
                                self.send_inst = False
                                # break from pygame event
                                break

                        # when the key were lifted loop back
                        elif event.type == pygame.KEYUP:
                            
                            # break from pygame event
                            break

            # list all content exist inside the apv.tempfolder00 directory
            temp_subfolder_filelist = os.listdir(apv.folder00 + "/" + apv.tempfolder00)
            
            # move apv.tempfolder00 content to apv.folder01
            for a in temp_subfolder_filelist:

                shutil.move(apv.folder00 + "/" + apv.tempfolder00 + "/" + a, apv.folder00 + "/" + apv.folder01)
            
            # delete apv.tempfolder00
            shutil.rmtree(apv.folder00 + "/" + apv.tempfolder00)
            # list all content exist inside the apv.tempfolder01 directory
            temp_folder_filelist = os.listdir(apv.folder00 + "/" + apv.tempfolder01)
            
            # move apv.tempfolder01 content to apv.folder02
            for b in temp_folder_filelist:

                shutil.move(apv.folder00 + "/" + apv.tempfolder01 + "/" + b, apv.folder00 + "/" + apv.folder02)
            
            #delete temp_subfolder
            shutil.rmtree(apv.folder00 + "/" + apv.tempfolder01)

            # if apv.file00 didn't exist save a new one
            if not os.path.exists(apv.folder00 + "/" + apv.folder02 + '/' + apv.file00):
            
                # save input data as .npz
                train_labels = label_array[1:, :]
                np.savez(apv.folder00 + "/" + apv.folder02 + '/' + apv.file00, train_labels = train_labels)

            # else if .npz already exist concatenate with new one
            else:
                
                # save input data as tmp.npz
                train_labels = label_array[1:, :]
                np.savez(apv.folder00 + "/" + apv.folder02 + apv.tempfile00, train_labels = train_labels)
                # load the original apv.file00
                data1 = load(apv.folder00 + "/" + apv.folder02 + '/' + apv.file00)
                # list the content inside data1
                lst1 = data1.files

                # for all the content exist inside the apv.file00
                for item in lst1:
                    
                    # load the data as tuple a
                    a = (data1[item])
                    # close data1
                    data1.close()

                # delete the apv.file00
                os.remove(apv.folder00 + "/" + apv.folder02 + '/' + apv.file00)
                # load the apv.tempfile00
                data2 = load(apv.folder00 + "/" + apv.folder02 + apv.tempfile00)
                # list the content inside data2
                lst2 = data2.files
                
                # for all the content exist inside the apv.tempfile00
                for item in lst2:    
    
                    # load the data as tuple a
                    b = (data2[item])
                    # close data2
                    data2.close()

                # delete the apv.tempfile00
                os.remove(apv.folder00 + "/" + apv.folder02 + apv.tempfile00)
                # concatenate 2 tuples into 1 tuple
                c = np.concatenate((a, b), 0)
                # save the concatenate tuple into .npz
                np.savez(apv.folder00 + "/" + apv.folder02 + '/' + apv.file00, train_labels = c)
            
            # click counter
            print("\n\n[Click counter]")
            print("» Forward clicks: ", clicks_forward)
            print("» Forward-left clicks: ", clicks_forward_left)
            print("» Forward-right clicks: ", clicks_forward_right)

            # frame counter
            print("\n[Frame counter]")
            print("» Total frame: ", total_frame)
            print("» Saved frame: ", saved_frame)
            print("» Dropped frame: ", total_frame - saved_frame, "\n")

        except:

            # if error occured do nothing
            pass
        
        else:

            # turn on the killswitch2
            switch.killswitch2()
            # rest for 0.4 second
            time.sleep(0.4)
            # close steer data collect nicely
            self.connection.close()
            self.server_socket.close

# threading 2; create a class for futaba controller client
class ControllerClient(threading.Thread):

    # initialize threading 2, client socket address and port
    def __init__(self, host2, port2):

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

        # execute kill switch checking
        self.sending()

    # when connection with server is established
    def sending(self):

        try:

            # while loop
            while True:

                # if kill switch for threading 2 is activated
                if (LatchingSwitch.tr_alive != True):

                    # raise exception
                    raise Exception

                # read steer_command shared variable from threading1
                input = SteerDataCollect.steer_command

                # if input is None
                if (input == None):

                    # break from while loop
                    break

                # else if input value is not 5
                elif (input != 5):

                    # send command to rover to brake
                    if (input == 0):

                        self.client_socket.send('0'.encode())
                        

                    # send command to rover to move forward
                    elif (input == 1):
                            
                        self.client_socket.send('1'.encode())
                        print ("Saved: ↑")

                    # send command to rover to turn right
                    elif (input == 2):
                                
                        self.client_socket.send('2'.encode())
                        print ("Saved: →")

                    # send command to rover to turn left
                    elif (input == 3):
                                
                        self.client_socket.send('3'.encode())
                        print ("Saved: ←")

                    # send command to rover to move backward
                    elif (input == 4):
                                
                        self.client_socket.send('4'.encode())

                    # rest for 0.4 second
                    time.sleep(0.3)
                
                # else if input is 5
                elif (input == 5):

                    # rest for 0.1 second
                    time.sleep(0.1)

        except:

            # do nothing
            pass

        else:

            # quit futaba controller server nicely
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

# step 2; initialize latching switch to communicate with threading 1, 2
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

        # assign switches value to false
        LatchingSwitch.tr_alive = None

# step 3; control latching switch condition and manage individual threading 1, 2
class ThreadingManager(object):

    # LatchingSwitch class is now switch
    switch = LatchingSwitch()

    try:

        # clear the screen
        os.system("cls")
        # print out info for user
        print ("Data are going to be collected and saved in /%s/%s/ folder for original" % (apv.folder00, apv.folder01))
        print ("image and /%s/%s/ folder for filtered images. Meanwhile collected" % (apv.folder00, apv.folder02))
        print ("user input will be saved in /%s/%s/ folder only." % (apv.folder00, apv.folder02))
        print ("\nData will be saved automatically if the user press ↑, → and ← keys on Pygame window.")
        print ("To stop before TCP connection is established press [CTRL] + [c] on console, to stop")
        print ("after TCP connection is established press [q] on Pygame windows.")
        # get user input
        input ("\nTo start press [Enter].")
        # set classes as threadings
        tr1 = threading.Thread(target = SteerDataCollect, args = (apv.pc, apv.video))
        tr2 = threading.Thread(target = ControllerClient, args = (apv.rpi, apv.controller))
        # set threadings as daemon
        tr1.daemon = True
        tr2.daemon = True
        # set classes as threadings
        tr1.start()
        tr2.start()
        # print out info for user
        print ("\nThreading start, waiting connection from RPi side.\n")

        # check threading 1, 2 to see if it is alive or not
        while True:

            # if recording is completed
            if (switch.tr_alive == None):

                # break from while loop
                break

            # else if threading1 is dead
            elif ((tr1.is_alive() != True) and (tr2.is_alive() == True)):

                # print the message
                print ("\nSteer data collect threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading2 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() != True)):

                # print the message
                print ("\nFutaba controller client threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if all threading is dead
            elif ((tr1.is_alive() != True) and (tr2.is_alive() != True)):

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

        # turn on the killswitch1
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