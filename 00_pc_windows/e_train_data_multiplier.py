#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules being used in the program
import a_prefix_variable as apv
from datetime import datetime
from numpy import load
import numpy as np
import shutil
import glob
import cv2
import sys
import os

# check os compatibility
if (os.name != 'nt'):

    print ("\nThis code is only compatible with Windows OS!\n")
    exit()

# check python environment compatibility
if (sys.version_info[0] < 3):

    print ("\nThis code is only compatible with Python 3 environment!\n")
    exit()

# if apv.folder01 doesn't exist end the program
if not os.path.exists(apv.folder00 + "/" + apv.folder01):

    print ("\nFolder /%s/%s/ where the image files supposedly located does not exist!\n" % (apv.folder00, apv.folder01))
    exit()

# if apv.folder02 doesn't exist end the program
if not os.path.exists(apv.folder00 + "/" + apv.folder02):

    print ("\nFolder /%s/%s/, where the training data supposedly located does not exist!\n" % (apv.folder00, apv.folder02))
    exit()

# delete apv.folder07 if it exist
if os.path.exists(apv.folder05 + "/" + apv.folder07):

    shutil.rmtree(apv.folder05 + "/" + apv.folder07)

# create a blank apv.folder07
os.makedirs(apv.folder05 + "/" + apv.folder07)

# delete apv.folder03 if it exist
if os.path.exists(apv.folder03):
                    
    shutil.rmtree(apv.folder03)

# create new folder3 path
os.makedirs(apv.folder03)

# while loop
while True:

    try:

        # clear screen
        os.system("cls")
        # print out info for user
        print ("This program double the collected training data needed to train the self-steer AI and sign recognition AI.")
        print ("The doubled negative data will be saved in /%s/%s/ folder." % (apv.folder05, apv.folder07))
        print ("The doubled steer data will be saved in /%s/ folder." % apv.folder03)
        print ("\nPick the task you want to run.")
        print ("[1] Double the data.")
        print ("[2] Quit.")
        # get user input
        pick = int(input ("\nYour pick: "))

        # if pick is 1
        if (pick == 1):

            # list all content exist inside the apv.folder02 directory
            filelist1 = os.listdir(apv.folder00 + "/" + apv.folder02)

            # copy apv.folder02 content to apv.folder03
            for a in filelist1:

                shutil.copy(apv.folder00 + "/" + apv.folder02 + "/" + a, apv.folder03)

            # load the filtered images location
            training_filtered = glob.glob(apv.folder03 + "/" + "*.jpg")
            # load the tuple from apv.file00 file
            original = load(apv.folder03 + "/" + apv.file00)
            # save images location as array
            image_filtered = np.array([cv2.imread(file) for file in training_filtered])
            # find how many images exist inside image_filtered
            filtered_size = len(image_filtered)
            # print out the images count
            print("\n%s filtered images need to be flipped.\n" % filtered_size)

            # flip the filtered images and save it to designated folder
            for x in range(filtered_size):

                # get the current time
                timestr = datetime.now().strftime("%Y%m%d%H%M%S%f")
                # flip the image and save
                flipped_filtered = np.flip(image_filtered[x], 1)
                # print filename
                print ("%s.jpg" % timestr)
                # save image to specified folder
                cv2.imwrite(apv.folder03 + "/" + timestr + '.jpg', flipped_filtered)

            # list the content inside the apv.file00
            lst = original.files
            
            # for all the content exist inside the apv.file00
            for item in lst: 

                # load into a
                a = (original[item])

            # print out array's object count
            print ("\n%s arrays of tuple need to be flipped.\n" % len(a))
            # flip the tuple
            b = np.flip(a, 1)
            # concatenate tuple a and b
            c = np.concatenate((a, b), 0)
            # save concatenate tuple as apv.file00
            np.savez(apv.folder03 + "/" + apv.file00, train_labels = c)
            # list all content exist inside the apv.folder01 directory
            filelist2 = glob.glob(apv.folder00 + "/" + apv.folder01 + "/" + "*.jpg")
            # find how many contents exist inside the array
            array_length = len(filelist2)
            # create bg.txt file
            bg_txt = open(apv.folder05 + "/" + "bg.txt",'w')
            # print out info to the user
            print ("\n%s negative image need to be flipped.\n" % array_length)

            # convert all the image in array as grayscale and save it as negative image
            for x in range(array_length):

                # get the current time
                timestr1 = datetime.now().strftime("%Y%m%d%H%M%S%f")
                # load the image on opencv
                color = cv2.imread(filelist2[x])
                # convert image to grayscale1
                grayscale1 = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
                # save the grayscale1 image as negative image
                cv2.imwrite(apv.folder05 + "/" + apv.folder07 + "/" + timestr1 + '.jpg', grayscale1)
                # print filename
                print ("%s.jpg" % timestr1)
                # get the current time
                timestr2 = datetime.now().strftime("%Y%m%d%H%M%S%f")
                # flip the grayscale1
                grayscale2 = np.flip(grayscale1, 1)
                # save the grayscale2 image as negative image
                cv2.imwrite(apv.folder05 + "/" + apv.folder07 + "/" + timestr2 + '.jpg', grayscale2)
                # save images path in bg.txt
                bg_txt.write(apv.folder07 + "/" + timestr1 + '.jpg' + "\n")
                bg_txt.write(apv.folder07 + "/" + timestr2 + '.jpg' + "\n")

            # close bg.txt
            bg_txt.close()
            # print out info to user
            print ("\nFlipped.")
            # print out the situation to user
            print ("\nMultiplier executed successfully.\n")
            # break from while loop
            break

        # if pick is 2
        elif (pick == 2):

            # print out the situation to user
            print ("\nDoubler canceled.\n")
            # break from while loop
            break

    # if pick is not number
    except ValueError:

        # pass back to while loop
        pass

    # if file does't exist
    except FileNotFoundError:

        # print info to user
        print ("\nFiles that need to be doubled doesn't exist.\n")
        # break from while loop
        break

    # if pick number is out of range
    else:

        # pass back to while loop
        pass