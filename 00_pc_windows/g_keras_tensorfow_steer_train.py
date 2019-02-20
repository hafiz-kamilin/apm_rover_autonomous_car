#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# import common modules
import a_prefix_variable as apv
from tqdm import tqdm
import pandas as pd
import numpy as np
import shutil
import glob
import json
import time
import csv
import cv2
import sys
import os

# import machine learning common modules
from keras.layers import Activation, Dense, Dropout, Flatten
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from keras.layers import Conv2D, MaxPooling2D
from keras.layers.core import Reshape
from keras.models import Sequential
from sklearn import preprocessing
from keras import regularizers
from keras import backend

# import machine learning model visualization modules
from keras.utils import plot_model
import matplotlib.pyplot as plt

# initialize user pick
pick_1 = None
pick_2 = 1
pick_3 = None

# check os compatibility
if (os.name != 'nt'):

    print ("\nThis codes only compatible with Windows OS!\n")
    exit()

# check python environment compatibility
if (sys.version_info[0] < 3):

    print ("\nThis codes only compatible with Python 3 environment!\n")
    exit()

# if apv.folder03 doesn't exist end the program
if not os.path.exists(apv.folder03):

    print ("\nFolder /%s/, where the training data supposedly located does not exist!\n" % apv.folder03)
    exit()

# create apv.folder04 if it doesn't exist
if not os.path.exists(apv.folder04):

    os.makedirs(apv.folder04)

# check if apv.tempfolder02 from previous unsuccessful or crashed execution exist
if os.path.exists(apv.folder04 + "/" + apv.tempfolder02):

    # delete apv.tempfolder02
    shutil.rmtree(apv.folder04 + "/" + apv.tempfolder02)

# check if apv.tempfolder03 from previous unsuccessful or crashed execution exist
if os.path.exists(apv.folder04 + "/" + apv.tempfolder03):

    # delete apv.tempfolder03
    shutil.rmtree(apv.folder04 + "/" + apv.tempfolder03)

# loop until correct number is entered
while True:

    try:

        # clear screen
        os.system("cls")
        # print out info for user
        print ("This program will train artificial intelligence to steer the RC car based on steer data recorded by the")
        print ("user. This program also contain multiple mode such as in depth post training analysis,")
        print ("multiple rounds of training and changeable optimization mode.")
        print ("\nPick which execution mode you would like to run.")
        print ("[1] Single round post training analysis.")
        print ("[2] Multiple rounds of training.")
        print ("[3] quit.")
        # get user input
        pick_1 = int(input ("\nYour pick: "))

        # if pick_1 is 1
        if (pick_1 == 1):

            # print info to user
            print ("\nSingle round post training analysis mode was selected.")
            # break from while loop
            break

        # if pick_1 is 2
        elif (pick_1 == 2):

            while True:

                try:

                    # print info to user
                    print ("\nMultiple rounds of training mode was selected.")
                    print ("\nplease enter any number from [1], [2], ..., [9].")
                    print ("To quit enter number [10].")
                    pick_2 = int(input ("\nYour number: "))

                    # if number is in range of 1 to 9
                    if ((pick_2 > 0) and (pick_2 < 10)):
                        
                        # break from while loop
                        break

                    # else if number is 10
                    elif (pick_2 == 10):

                        # exit from the program
                        exit()

                # if pick is not number
                except ValueError:

                    # pass back to while loop
                    pass

                # if pick number is out of range
                else:

                    # pass back to while loop
                    pass
            
            # break from while loop
            break

        # else if pick_1 is 3
        elif (pick_1 == 3):

            # exit from the program
            exit()

    # if pick is not number
    except ValueError:

        # pass back to while loop
        pass

    # if pick number is out of range
    else:

        # pass back to while loop
        pass

# loop until correct number is entered
while True:

    try:

        # print out info for user
        print ("\nPick which optimization mode you would like to run.")
        print ("[1] Adadelta optimization.")
        print ("[2] Adagard optimization.")
        print ("[3] RMSProp optimization.")
        print ("[4] Adamax optimization.")
        print ("[5] Nadam optimization.")
        print ("[6] Adam optimization.")
        print ("[7] SGD optimization.")
        print ("[8] quit.")
        # get user input
        pick_3 = int(input ("\nYour pick: "))

        # if pick_3 is 1 to 7
        if ((pick_3 > 0) and (pick_3 < 8)):

            # break from while loop
            break

        # else if pick_3 is 8
        elif (pick_3 == 8):

            # exit from the program
            exit()

    # if pick is not number
    except ValueError:

        # pass back to while loop
        pass

    # if pick number is out of range
    else:

        # pass back to while loop
        pass

# print instruction
print ("\nTo quit at anytime press [CTRL] + [C].")
# rest for 5 seconds
time.sleep(5)
# get the start time when the program start
time_program_start = time.time()
# create apv.tempfolder03 to temporary store model weight by round
os.makedirs(apv.folder04 + "/" + apv.tempfolder03)

try:

    # repeat training for the number of pick_2
    for a in range(pick_2):

        # create apv.tempfolder02 file to temporary store model weight by epoch
        os.makedirs(apv.folder04 + "/" + apv.tempfolder02)
        # print the counted number
        print ("\nThe number of training round left is %s." % (pick_2 - (a + 1)))
        # print action that will be executed
        print ("\nLoad images and tuple from .npz to be trained.")
        # load jpg images to get image_array
        training_images = glob.glob(apv.folder03 + "/*.jpg")
        # progress bar
        image_array = np.array([cv2.imread(name, cv2.IMREAD_GRAYSCALE) for name in tqdm(training_images, desc = "Image")], dtype =  np.float64)
        # Load .npz to get label_array
        training_data = glob.glob(apv.folder03 + "/*.npz")
        label_array = None
        # unpacking the .npz content
        for single_npz in training_data:
            
            # single_npz == one array representing one array of saved user input label for that image
            with np.load(single_npz) as data:
                
                # returns the training user input data array assigned to 'train_labels' argument
                train_labels_temp = data["train_labels"]
            
            # progress bar
            label_array = np.array([label for label in tqdm(train_labels_temp, desc = "Array")], dtype=np.float64)

        # save image_array and label_array into X and y
        X = image_array
        y = label_array
        # normalize from 0 to 1
        X = X / 255.
        # print sample and test parameter
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.10)
        print ("\nNumber of sample and test data for this training")
        print ("» %s sample images with %s pixels of height and %s pixel of width" % (X_train.shape[0], X_train.shape[1], X_train.shape[2]))
        print ("» %s test image with %s pixels of height and %s pixel of width" % (X_test.shape[0], X_test.shape[1], X_test.shape[2]))
        print ("» %s of sample input saved in array size of %s" % (y_train.shape[0], y_train.shape[1]))
        print ("» %s of test input saved in array size of %s" % (y_test.shape[0], y_test.shape[1]))
        # initialising the cnn
        model = Sequential()
        # using tensorflow backend
        model.add(Reshape((120, 320, 1), input_shape = (120, 320), name = "input"))
        # first convolutional layer and pooling
        model.add(Conv2D(32, (5, 5), padding = "same", activation = "relu", name = "1st_cnn_layer"))
        model.add(MaxPooling2D(pool_size = (2, 2)))
        # second convolutional layer and pooling (default parameter for regularizer: kernel_regularizer = regularizers.l2(0.01))
        model.add(Conv2D(32, (5, 5), kernel_regularizer = regularizers.l2(0.0001), activation = "relu", name = "2nd_cnn_layer"))
        model.add(MaxPooling2D(pool_size = (2, 2)))
        # third convolutional layer and pooling (default parameter for regularizer: activity_regularizer = regularizers.l1(0.01))
        model.add(Conv2D(32, (5, 5), activity_regularizer = regularizers.l1(0.00001), activation = "relu", name = "3rd_cnn_layer"))
        model.add(MaxPooling2D(pool_size = (2, 2)))
        # flatten, fully connected layer 1 (14,208 to 28,416 nodes)
        model.add(Flatten(name = "1st_fully_connected_layer"))
        model.add(Dropout(0.20))
        # fully connected layer 2 (300 nodes)
        model.add(Dense(300, kernel_initializer = "uniform", name = "2nd_fully_connected_layer"))
        model.add(Activation("relu"))
        # output layer (3 nodes)
        model.add(Dense(3, kernel_initializer = "uniform", name = "output_layer"))
        model.add(Activation("softmax"))

        # adadelta type of optimization
        if (pick_3 == 1):

            print ("\nAdadelta optimizer selected.\n")
            from keras.optimizers import Adadelta
            adadelta = Adadelta(lr = 1.0, rho = 0.95, epsilon = None, decay = 0.0)
            model.compile(loss = "categorical_crossentropy", 
                                optimizer = adadelta,
                                metrics = ["accuracy"])

        # adagard type of optimization
        elif (pick_3 == 2):

            print ("\nAdagard optimizer selected.\n")
            from keras.optimizers import Adagrad
            adagard = Adagrad(lr = 0.01, epsilon = None, decay = 0.0)
            model.compile(loss = "categorical_crossentropy",
                        optimizer = adagard,
                        metrics = ["accuracy"])

        # rmsprop type of optimization
        elif (pick_3 == 3):

            print ("\nRMSProp optimizer selected.\n")
            from keras.optimizers import RMSprop
            rmsprop = RMSprop(lr = 0.001, rho = 0.9, epsilon = None, decay = 0.0)
            model.compile(loss = "categorical_crossentropy",
                        optimizer = rmsprop,
                        metrics = ["accuracy"])

        # adamax type of optimization
        elif (pick_3 == 4):

            print ("\nAdamax optimizer selected.\n")
            from keras.optimizers import Adamax
            adamax = Adamax(lr = 0.002, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0.0)
            model.compile(loss = "categorical_crossentropy",
                        optimizer = adamax,
                        metrics = ["accuracy"])

        # nadam type of optimization
        elif (pick_3 == 5):

            print ("\nNadam optimizer selected.\n")
            from keras.optimizers import Nadam
            nadam = Nadam(lr = 0.002, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, schedule_decay = 0.004)
            model.compile(loss = "categorical_crossentropy",
                        optimizer = nadam,
                        metrics = ["accuracy"])

        # adam type of optimization
        elif (pick_3 == 6):

            print ("\nAdam optimizer selected.\n")
            from keras.optimizers import Adam
            adam = Adam(lr = 0.001, beta_1 = 0.9, beta_2 = 0.999, epsilon = None, decay = 0.0, amsgrad = False)
            model.compile(loss = "categorical_crossentropy",
                        optimizer = adam,
                        metrics = ["accuracy"])

        # sgd type of optimization
        elif (pick_3 == 7):

            print ("\nSGD optimizer selected.\n")
            from keras.optimizers import SGD
            sgd = SGD(lr = 0.01, decay = 1e-6, momentum = 0.9, nesterov = True)
            model.compile(loss = "categorical_crossentropy",
                        optimizer = sgd,
                        metrics = ["accuracy"])

        # set callback functions to early stop training
        callbacks = [EarlyStopping(monitor = 'val_loss', min_delta = 0, patience = 3, verbose = 0, mode = 'auto'),
                    ModelCheckpoint(filepath = apv.folder04 + "/" + apv.tempfolder02 + "/valloss{val_loss:.4f}_valaccu{val_acc:.4f}.h5", monitor = 'val_loss', verbose = 0, save_best_only = True, mode = 'auto', period = 1)]
        # fit the model
        history = model.fit(X_train, y_train,
                epochs = 20,
                batch_size = 20,
                callbacks = callbacks,
                validation_data = (X_test, y_test))

        # if pick_1 is 1
        if (pick_1 == 1):

            # save keras_tf cnn model overview
            plot_model(model, to_file = apv.folder04 + "/model_overview.png", show_shapes = True, show_layer_names = True)
            # plot training and validation accuracy values
            plt.plot(history.history['acc'])
            plt.plot(history.history['val_acc'])
            plt.title('History for model accuracy')
            plt.ylabel('Accuracy')
            plt.xlabel('Epoch')
            plt.legend(['Train', 'Test'], loc = 'upper left')
            plt.savefig(apv.folder04 + "/model_accuracy.png")
            plt.show()
            # plot training and validation loss values
            plt.plot(history.history['loss'])
            plt.plot(history.history['val_loss'])
            plt.title('History for model loss')
            plt.ylabel('Loss')
            plt.xlabel('Epoch')
            plt.legend(['Train', 'Test'], loc = 'upper left')
            plt.savefig(apv.folder04 + "/model_loss.png")
            plt.show()

        # destroys the current tf graph and creates a new one
        backend.clear_session()
        # list all h5 files exist in apv.tempfolder02 in an array
        h5_filelist = glob.glob(apv.folder04 + "/" + apv.tempfolder02 + "/*.h5")
        # in ascending order pick only the first file (from naming scheme, the best model weight will be listed first in array)
        best_h5_file = h5_filelist[0]
        # move the best h5 file into apv.tempfolder03
        shutil.move(best_h5_file, apv.folder04 + "/" + apv.tempfolder03)
        # delete apv.tempfolder02
        shutil.rmtree(apv.folder04 + "/" + apv.tempfolder02)

# if [CTRL] + [c] is pressed
except KeyboardInterrupt:

    # print info to user
    print ("\n[CTRL] + [c] is pressed.\n")
    # exit from the program
    exit()

# if image does't exist
except FileNotFoundError:

    # print info to user
    print ("\nFile that need to be opened doesn't exist.\n")
    # exit from the program
    exit()

# if npz does't exist
except IndexError:

    # print info to user
    print ("\nFile that need to be opened doesn't exist.\n")
    # exit from the program
    exit()

# if no error
else:

    # list all h5 files exist in apv.tempfolder03 in an array
    h5_filelist = glob.glob(apv.folder04 + "/" + apv.tempfolder03 + "/*.h5")
    # in ascending order pick only the first data saved in array (from naming scheme, the best model weight will be listed first)
    best_h5_file = h5_filelist[0]
    # move the best h5 file into folder1
    shutil.move(best_h5_file, apv.folder04 + "/")
    #delete temp_subfolder1
    shutil.rmtree(apv.folder04 + "/" + apv.tempfolder03)
    # get the end time when the program end
    time_program_end = time.time()
    # calculate total time taken to run the program
    time_program_total = time_program_end - time_program_start
    # print the outcome detail
    print ("\nTotal time taken to train %s weight models is %s [s]." % (pick_2, int(time_program_total)))
    print ("The best model weight is saved at /%s/ folder along with previously generated best model weight.\n" % apv.folder04)