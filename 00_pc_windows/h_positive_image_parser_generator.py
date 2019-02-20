#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules used in the program
import a_prefix_variable as apv
import subprocess
import shutil
import glob
import sys
import os

# check os compatibility
if (os.name != 'nt'):

    print ("\nThis codes only compatible with Windows OS!\n")
    exit()

# check python environment compatibility
if (sys.version_info[0] < 3):

    print ("\nThis codes only compatible with Python 3 environment!\n")
    exit()

# if apv.folder06 doesn't exist end the program
if not os.path.exists(apv.folder05 + "/" + apv.folder06):

    print ("\nFolder /%s/%s/ where the template object image file supposedly located does not exist!\n" % (apv.folder05, apv.folder06))
    exit()

# if apv.folder07 doesn't exist end the program
if not os.path.exists(apv.folder05 + "/" + apv.folder07):

    print ("\nFolder /%s/%s/ where the negative images file supposedly located does not exist!\n" % (apv.folder05, apv.folder07))
    exit()

# delete apv.folder08 if it exist
if os.path.exists(apv.folder05 + "/" + apv.folder08):

    shutil.rmtree(apv.folder05 + "/" + apv.folder08)

# create a blank apv.folder08
os.makedirs(apv.folder05 + "/" + apv.folder08)

# clear screen
os.system("cls")
# print out info for user
print ("This Python program will utilize opencv_createsamples to generate positive image that")
print ("contain object to be recognize by using Haar Cascade classifier. Remember that")
print ("This program is a parser to streamline the opencv_createsamples usage.")
print ("It can't catch error occured on opencv_createsamples program.")

try:

    # print out info about opencv_createsamples
    print ("\nPlease type the opencv_createsamples location (e.g. C:/opencv/build/x64/vc15/bin/opencv_createsamples.exe).")
    print ("If you haven't installed OpenCV full package, download it from https://opencv.org/releases.html.")
    # get user input
    opencv_createsamples = str(input ("Location: "))
    # print out info about template object
    print ("\nPlease type the template object image filename (e.g. move.png/stop.png).")
    print ("Do note that the image must have at least 60x60 pixels.")
    # get user input
    template_object = str(input ("Filename: "))
    # separator
    print ("\n")
    # list all the image files that exist in apv.folder07
    negative_list = glob.glob(apv.folder05 + "/" + apv.folder07 + "/" + "*.jpg")
    # find how many images exist in apv.folder07
    negative_count = str(len(negative_list))
    # command_1 string
    command_1 = [opencv_createsamples, "-img", apv.folder05 + "/" + apv.folder06 + "/" + template_object, "-bg", apv.folder05 + "/" + "bg.txt", 
    "-info", apv.folder05 + "/" + apv.folder08 + "/" + "info.lst", "-info", "04_cascade_datasets/02_positive_object/info.lst", 
    "-pngoutput", "info", "-maxxangle", "1.1", "-maxyangle", "1.1", "-maxzangle", "0.5", "-num", negative_count]
    # run opencv_createsamples with command_1 string
    subprocess.run(command_1)
    # command_2 string
    command_2 = [opencv_createsamples, "-info", apv.folder05 + "/" + apv.folder08 + "/" + "info.lst", "-num", 
    negative_count, "-w", "20", "-h", "20", "-vec", apv.folder05 + "/" + "positives.vec"]
    # run opencv_createsamples with command_2 string
    subprocess.run(command_2)

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

else:

    # print info to user
    print ("\nPositive image parser generator ended.\n")