#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules used in the program
import a_prefix_variable as apv
from datetime import datetime
from socket import socket
import numpy as np
import threading
import socket
import glob
import time
import copy
import cv2
import sys
import os

# import machine learning modules
from keras.layers import Dense, Activation
from keras.models import Sequential
import keras.models

# threading 1; create a class for raspberry pi camera module server
class VideoStreamServer(threading.Thread):

    # initialize shared data variable
    color = None
    grayscale = None

    # initialize threading 1, server socket address and port
    def __init__(self, host1, port1):

        # assign value to shared data variable
        VideoStreamServer.color = []
        VideoStreamServer.grayscale = []
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

                # if kill switch for threading is activated
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
                    # change jpg stream into image
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    #  save it into shared variable
                    VideoStreamServer.color = image[120:240, :]
                    VideoStreamServer.grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    # print time taken to prepare 1 image
                    print ("Reference frames take %.3f [s] to complete" % (time.time() - start))

        except:

            # do nothing
            pass

        else:

            # close VideoStreamServer
            self.connection.close()
            self.server_socket.close()

# threading 2; create a class for haar cascade classifier to detect signs
class HaarCascadeClassifier(threading.Thread):

    # initialize shared data variable
    sign = None
    found = None

    # initialize threading 2
    def __init__(self):

        # if the apv.folder09 path doesn't exist
        if not os.path.exists(apv.folder09):

            print ("\nFolder /%s/, where the .xml files supposedly located does not exist!\n" % apv.folder09)
            raise Exception

        # assign value to shared data variable
        HaarCascadeClassifier.sign = []
        HaarCascadeClassifier.found = 1
        # 止 sign recognition cascade classifier
        self.stop_classifier = cv2.CascadeClassifier(apv.folder09 + "/" + apv.stop)
        # 動 sign recognition cascade classifier
        self.move_classifier = cv2.CascadeClassifier(apv.folder09 + "/" + apv.move)

        # while VideoStreamServer.grayscale is still empty
        while (VideoStreamServer.grayscale == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break
            
            # rest for 0.1 second
            time.sleep(0.1)

        # execute sign detection
        self.search()

    # define stop sign detection method
    def search(self):

        try:

            # while loop
            while True:

                # if kill switch for threading is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # create a grayscale image for haar cascade classifier
                image = np.copy(VideoStreamServer.grayscale)

                # find (止) stop in image
                stop = self.stop_classifier.detectMultiScale(

                    image,
                    scaleFactor = 1.1,
                    minNeighbors = 7,
                    minSize = (30, 30),
                    maxSize = (80, 80))

                # find (動) move in image
                move = self.move_classifier.detectMultiScale(
                    
                    image,
                    scaleFactor = 1.1,
                    minNeighbors = 7,
                    minSize = (30, 30),
                    maxSize = (80, 80))

                # convert 1 channel gray image to 3 channels gray image
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                
                # if (止) stop was found
                if np.any(stop):

                    # print result
                    print ("止 sign was found")
                    # change HaarCascadeClassifier.found value to 2
                    HaarCascadeClassifier.found = 2

                    # draw square if (止) stop was found
                    for (x, y, w, h) in stop:

                        # draw square
                        cv2.rectangle(image, (x + 5, y + 5), (x + w - 5, y + h - 5), (0, 255, 0), 2)
                        # draw text
                        cv2.putText(image, "Stop sign", (x, y + h + 10), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 255, 0), 2)

                    # copy the image to a shared variable
                    HaarCascadeClassifier.sign = np.copy(image)
                    # resume the loop back at start
                    continue

                # if (動) move was found
                elif np.any(move):

                    # print result
                    print ("動 sign was found")
                    # change HaarCascadeClassifier.found value to 1
                    HaarCascadeClassifier.found = 1

                    # draw square if (動) move was found
                    for (x, y, w, h) in move:

                        # draw square
                        cv2.rectangle(image, (x + 5, y + 5), (x + w - 5, y + h - 5), (0, 255, 0), 2)
                        # draw sign
                        cv2.putText(image, 'Move sign', (x, y + h + 10), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 255, 0), 2)

                    # copy the image to a shared variable
                    HaarCascadeClassifier.sign = np.copy(image)
                    # resume the loop back at start
                    continue

                # if nothing was found
                else:

                    # print result
                    print ("No sign was found")
                    # put text on image
                    cv2.putText(image, "No sign", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 255, 0), 2)
                    # copy the image to a shared variable
                    HaarCascadeClassifier.sign = np.copy(image)

        except:

            # do nothing
            pass

# threading 3; create a class for keras to detect road features
class KerasConvolutionalLayers(threading.Thread):

    # initialize shared data variable
    road = None
    command = None

    # initialize threading 3
    def __init__(self):

        # if the apv.folder04 path doesn't exist
        if not os.path.exists(apv.folder04):

            print ("\nFolder /%s/, where the .h5 files supposedly located does not exist!\n" % apv.folder04)
            raise Exception

        # assign value to shared data variable
        KerasConvolutionalLayers.road = []
        KerasConvolutionalLayers.command = 0
        # list all h5 files exist in folder/subfolder0 in an array
        h5_filelist = glob.glob(apv.folder04 + "/" + "*.h5")
        # list the files in ascending order and pick the best
        self.model = keras.models.load_model(h5_filelist[0])

        # while VideoStreamServer.color is still empty
        while (VideoStreamServer.color == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break
            
            # rest for 0.1 second
            time.sleep(0.1)

        # execute sign detection
        self.steer()

    # custom edge canny detection
    def canny(self, blur):
        
        # sigma value for edge canny detection
        SIGMA = apv.sigma
        # compute the median of the single channel pixel intensities
        median = np.median(blur)
        # apply custom canny edge detection using the computed median of the image
        lower = int(max(0,   (1.0 - SIGMA) * median))
        upper = int(min(255, (1.0 + SIGMA) * median))
        edged = cv2.Canny(blur, lower, upper)
        # return filtered image
        return edged

    # preprocess image frame
    def preprocess(self, frame):

        # reshape image array to be feed into neural network
        image_array = frame.reshape(1, 120, 320).astype(np.float32)
        image_array = image_array / 255.
        # return preprocessed image
        return image_array

    # prediction
    def predict(self, image):

        # get the preprocessed image
        image_array = self.preprocess(image)
        # get the steer prediction
        y_hat = self.model.predict(image_array)
        i_max = np.argmax(y_hat)
        y_hat_final = np.zeros((1,3))
        np.put(y_hat_final, i_max, 1)
        # return the result in form of array
        return y_hat_final[0]

    # define steering based on detected road features
    def steer(self):

        try:

            # while loop
            while True:

                # if kill switch for threading is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get a copy of image from VideoStreamServer
                image = np.copy(VideoStreamServer.color)
                # apply gaussian blur to reduce noise
                image = cv2.GaussianBlur(image, (3, 3), 0)
                # apply custom canny edge filter
                image = self.canny(image)
                # predict the road features
                prediction = self.predict(image)
                # initialize result text
                result_ascii = None
                result_unicode = None
                # convert 1 channel gray image to 3 channels gray image
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

                # if prediction is forward
                if np.all(prediction == [ 0., 1., 0.]):

                    # add string result
                    result_ascii = "forward"
                    result_unicode = "↑"
                    # set command to 1
                    KerasConvolutionalLayers.command = 1

                # else if prediction is right
                elif np.all(prediction == [ 0., 0., 1.]):

                    # add string result
                    result_ascii = "right"
                    result_unicode = "→"
                    # set command to 2
                    KerasConvolutionalLayers.command = 2

                # else if prediction is left
                elif np.all(prediction == [ 1., 0., 0.]):

                    # add string result
                    result_ascii = "left"
                    result_unicode = "←"
                    # set command to 3
                    KerasConvolutionalLayers.command = 3

                # print out the result
                print ("Steer %s" % result_unicode)
                # put text on image
                cv2.putText(image, "Move {}".format(result_ascii), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .50, (255, 0, 0), 2)
                # copy the image to shared variable
                KerasConvolutionalLayers.road = np.copy(image)

        except:

            # do nothing
            pass

# threading 4; create a class for lidar rangefinder server
class RangeFinderServer(threading.Thread):
    
    # initialize shared data variable
    brake = None
    warning = None

    # initialize threading 4, server socket address and port
    def __init__(self, host2, port2):

        # assign value to shared data variable
        RangeFinderServer.brake = True
        RangeFinderServer.warning = []
        # server socket and port
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host2, port2))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)

        # while VideoStreamServer.color is still empty
        while (VideoStreamServer.color == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break
            
            # rest for 0.1 second
            time.sleep(0.1)

        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # initialize distance_old to store previous distance reading
            distance_old = 1

            # while loop
            while True:

                # if kill switch for threading is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get a copy of image from VideoStreamServer
                image = np.copy(VideoStreamServer.color)
                # receive the distance reading from the client
                distance_new = int(self.connection.recv(1024).decode())

                # if distance is below treshold
                if ((distance_new > 0) and (distance_new <= 30)):

                    # change brake value to true
                    RangeFinderServer.brake = True
                    # put text on image
                    cv2.putText(image, "Emergency brake enabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 0, 255), 2)
                    # store current distance to distance_old
                    distance_old = distance_new
                    # print out the distance
                    print ("Distance in front is %d [cm]" % distance_new)
                    # print out the situation
                    print ("Emergency brake enabled")

                # else if distance is over treshold
                elif ((distance_new > 31) and (distance_new <= 50)):

                    # change brake value to false
                    RangeFinderServer.brake = False
                    # put text on image
                    cv2.putText(image, "Emergency brake disabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 0, 255), 2)
                    # store current distance to distance_old
                    distance_old = distance_new
                    # print out the distance
                    print ("Distance in front is %d [cm]" % distance_new)
                    # print out the situation
                    print ("Emergency brake disabled")

                # else if current distance received is broken use previous saved distance
                else:

                    # if RangeFinderServer.brake is true
                    if (RangeFinderServer.brake == True):

                        # put text on image
                        cv2.putText(image, "Emergency brake enabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 0, 255), 2)
                        # print out the distance
                        print ("Distance in front is %d [cm]" % distance_old)
                        # print out the situation
                        print ("Emergency brake enabled")

                    # if RangeFinderServer.brake is false
                    elif (RangeFinderServer.brake == False):

                        # put text on image
                        cv2.putText(image, "Emergency brake disabled", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .50, (0, 0, 255), 2)
                        # print out the distance
                        print ("Distance in front is %d [cm]" % distance_old)
                        # print out the situation
                        print ("Emergency brake disabled")

                # copy the image to shared variable
                RangeFinderServer.warning = np.copy(image)

        except:

            # do nothing
            pass

        else:

            # close RangeFinderServer
            self.connection.close()
            self.server_socket.close()

# threading 5; create a class for futaba controller client
class ControllerDriveClient(threading.Thread):

    # initialize threading 5, client socket address and port
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
        
        # while loop
        while True:
            
            # if shared found and command is still empty
            if (((HaarCascadeClassifier.found and KerasConvolutionalLayers.command) != 0) and (RangeFinderServer.brake != True)):
                
                # break
                break

            # rest for 0.1 second
            time.sleep(0.1)

        # execute client sending
        self.sending()

    # when connection with server is established
    def sending(self):

        # LatchingSwitch class is now switch
        switch = LatchingSwitch()

        try:

            # initialize self.arrow_switch to 0
            self.arrow_switch = 0
            # LatchingSwitch class is now switch
            switch = LatchingSwitch()

            # while loop
            while self.connected:

                # if kill switch for threading is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # if haar cascade found (止) stop sign or brake is activated
                if ((HaarCascadeClassifier.found == 2) or (RangeFinderServer.brake == True)):

                    # send command to brake via tcp connection
                    self.client_socket.send('0'.encode())

                # if default or haar cascade found (動) move sign and brake is disabled
                if ((HaarCascadeClassifier.found == 1) and ((RangeFinderServer.brake == False))):

                    # if road features indicate to move forward
                    if (KerasConvolutionalLayers.command == 1):
                            
                        # send command to move forward via tcp connection
                        self.client_socket.send('1'.encode())

                    # else if road features indicate to move right
                    elif (KerasConvolutionalLayers.command == 2):
                            
                        # send command to move right via tcp connection
                        self.client_socket.send('2'.encode())

                    # else if road features indicate to move left
                    elif (KerasConvolutionalLayers.command == 3):
                            
                        # send command to move left via tcp connection
                        self.client_socket.send('3'.encode())

                # print out the command
                print ("Control the RC car")

                # rest for 0.1 second
                time.sleep(0.1)

        except:

            # do nothing
            pass

        else:

            # close ControllerDriveClient
            self.client_socket.close()

# threading 6; create a class for image output
class SelfDrivingResult(threading.Thread):

    def __init__(self):

        # if the apv.folder09 path doesn't exist
        if not os.path.exists(apv.folder10):

            # create apv.folder10 folder
            os.makedirs(apv.folder10)

        # while shared images are still empty
        while (VideoStreamServer.color == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break

            # rest for 0.1 second
            time.sleep(0.1)

        # while shared images are still empty
        while (VideoStreamServer.grayscale == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break

            # rest for 0.1 second
            time.sleep(0.1)

        # while shared images are still empty
        while (RangeFinderServer.warning == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break

            # rest for 0.1 second
            time.sleep(0.1)

        # while shared images are still empty
        while (HaarCascadeClassifier.sign == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break

            # rest for 0.1 second
            time.sleep(0.1)
            
        # while shared images are still empty
        while (KerasConvolutionalLayers.road == []):

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break

            # rest for 0.1 second
            time.sleep(0.1)

        # execute result
        self.result()

    # combine multiple images into one
    def result(self):

        # LatchingSwitch class is now switch
        switch = LatchingSwitch()

        # while loop
        while True:

            # if kill switch for threading is activated
            if (LatchingSwitch.tr_alive != True):

                # break from while loop
                break
                
            # get the current time
            timestr = datetime.now().strftime("%Y%m%d%H%M%S%f")
            # concatenate the images into single image
            image = np.concatenate((RangeFinderServer.warning, HaarCascadeClassifier.sign, KerasConvolutionalLayers.road), axis = 0)
            # display the data stream as video
            cv2.imshow("To quit press [q].", image)

            # to close opencv windows press [q]
            if cv2.waitKey(1) & 0xFF == ord('q'):
                        
                # turn on the kill switch 2
                switch.killswitch2()
                # break from while loop
                break

            # save concatenate image to apv.folder10
            cv2.imwrite(apv.folder10 + '/' + '{}.jpg'.format(timestr), image)
            # rest for 0.1 [s]
            time.sleep(0.1)

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
        print ("This Python program will run trained Keras convolutional layers to steer the RC car and")
        print ("Haar Cascade Classifier to detect the road sign to take the appropriate")
        print ("actions. Data will be saved on %s as image files." % apv.folder10)
        print ("\nTo stop before TCP connection is established press [CTRL] + [c] on console, to stop")
        print ("after TCP connection is established press [q] on OpenCV windows.")
        # get user input
        input ("\nTo start press [Enter].")
        # set classes as threadings
        tr1 = threading.Thread(target = VideoStreamServer, args = (apv.pc, apv.video))
        tr2 = threading.Thread(target = HaarCascadeClassifier, args = ())
        tr3 = threading.Thread(target = KerasConvolutionalLayers, args = ())
        tr4 = threading.Thread(target = RangeFinderServer, args = (apv.pc, apv.rangefinder))
        tr5 = threading.Thread(target = ControllerDriveClient, args = (apv.rpi, apv.controller))
        tr6 = threading.Thread(target = SelfDrivingResult, args = ())
        # set threadings as daemon
        tr1.daemon = True
        tr2.daemon = True
        tr3.daemon = True
        tr4.daemon = True
        tr5.daemon = True
        tr6.daemon = True
        # start threadings
        tr1.start()
        tr2.start()
        tr3.start()
        tr4.start()
        tr5.start()
        tr6.start()
        # print out info for user
        print ("\nThreading start, waiting connection from RPi side.\n")

        # check threading 1, 2, 3 to see if it is alive or not
        while True:

            # if program ended properly
            if ((LatchingSwitch.tr_alive) == None):

                # break from while loop
                break

            # if threading1 is dead
            if ((tr1.is_alive() != True) and (tr2.is_alive() == True) and (tr3.is_alive() == True) and (tr4.is_alive() == True) and (tr5.is_alive() == True) and (tr6.is_alive() == True)):

                # print the message
                print ("\nVideoStreamServer threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading2 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() != True) and (tr3.is_alive() == True) and (tr4.is_alive() == True) and (tr5.is_alive() == True) and (tr6.is_alive() == True)):

                # print the message
                print ("\nHaarCascadeClassifier threading ended prepaturely.\n")
                # raise exception
                raise Exception

            # else if threading3 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() == True) and (tr3.is_alive() != True) and (tr4.is_alive() == True) and (tr5.is_alive() == True) and (tr6.is_alive() == True)):

                # print the message
                print ("\nKerasConvolutionalLayers threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading4 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() == True) and (tr3.is_alive() == True) and (tr4.is_alive() != True) and (tr5.is_alive() == True) and (tr6.is_alive() == True)):

                # print the message
                print ("\nRangeFinderServer threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading5 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() == True) and (tr3.is_alive() == True) and (tr4.is_alive() == True) and (tr5.is_alive() != True) and (tr6.is_alive() == True)):

                # print the message
                print ("\nControllerDriveClient threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading6 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() == True) and (tr3.is_alive() == True) and (tr4.is_alive() == True) and (tr5.is_alive() == True) and (tr6.is_alive() != True)):

                # print the message
                print ("\nSelfDrivingResult threading ended prematurely.\n")
                # raise exception
                raise Exception

            # if more than 1 threading is dead
            elif ((tr1.is_alive() != True) or (tr2.is_alive() != True) or (tr3.is_alive() != True) or (tr4.is_alive() != True) or (tr5.is_alive() != True) or (tr6.is_alive() != True)):

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