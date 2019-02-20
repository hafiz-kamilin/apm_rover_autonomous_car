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

# if apv.folder07 doesn't exist end the program
if not os.path.exists(apv.folder05 + "/" + apv.folder07):

    print ("\nFolder /%s/%s/ where the negative image files supposedly located does not exist!\n" % (apv.folder05, apv.folder07))
    exit()

# if apv.folder08 doesn't exist end the program
if not os.path.exists(apv.folder05 + "/" + apv.folder08):

    print ("\nFolder /%s/%s/ where the positive image files supposedly located does not exist!\n" % (apv.folder05, apv.folder08))
    exit()

# create a blank apv.tempfolder04 if it is not exist
if not os.path.exists(apv.folder05 + "/" + apv.tempfolder04):

    os.makedirs(apv.folder05 + "/" + apv.tempfolder04)

# clear screen
os.system("cls")
# print out info for user
print ("This Python program will utilize opencv_traincascade to generate xml file that")
print ("can be use to detect the trained object that exist on the picture. This")
print ("program is a parser to streamline the opencv_traincascade usage.")
print ("It can't catch error occured on opencv_traincascade program.")

try:
    
    # print out info about opencv_traincascade
    print ("\nPlease type the opencv_traincascade location (e.g. C:/opencv/build/x64/vc15/bin/opencv_traincascade.exe).")
    print ("If you haven't installed OpenCV full package, download it from https://opencv.org/releases.html.")
    # get user input
    opencv_traincascade = str(input ("Location: "))
    # print out info about round(s)
    print ("\nSpecify how many round(s) opencv_traincascade should train (e.g. [1], [2], ..... [n])?")
    # get user input
    round = str(input ("Round: "))
    # separator
    print ("\n")
    # list all the image files that exist in apv.folder07
    negative_list = glob.glob(apv.folder05 + "/" + apv.folder07 + "/" + "*.jpg")
    # count the negative image to be used in training
    negative_count = str(len(negative_list))
    # list all the image files that exist in apv.folder08
    positive_list = glob.glob(apv.folder05 + "/" + apv.folder08 + "/" + "*.jpg")
    # count the positive image to be used in training
    positive_count = str(len(positive_list) / 2)
    # change current process directory
    os.chdir(apv.folder05)
    # command string
    command = [opencv_traincascade, "-data", apv.tempfolder04, "-vec", "positives.vec", "-bg", "bg.txt", 
    "-numPos", positive_count, "-minHitRate", "0.999", "-mode", "ALL", "-numNeg", 
    negative_count, "-numStages", round, "-w", "20", "-h", "20"]
    # run command string as subprocess
    subprocess.run(command)
    # list all content exist inside the apv.tempfolder04 directory
    temp_folder04_filelist = os.listdir(apv.tempfolder04)
    # move apv.tempfolder04 content to folder01
    shutil.move(os.path.join(apv.tempfolder04, temp_folder04_filelist[0]), os.path.join("../", apv.folder09, temp_folder04_filelist[0]))
    # delete apv.tempfolder04
    shutil.rmtree(apv.tempfolder04)

# if image does't exist
except FileNotFoundError:

    # print info to user
    print ("\n\nFile that need to be opened doesn't exist.\n")
    # delete apv.tempfolder04
    shutil.rmtree(apv.tempfolder04)
    # exit from the program
    exit()

except KeyboardInterrupt:

    # print info to user
    print ("\n\n[CTRL] + [c] is pressed.\n")
    # exit from the program
    exit()

except shutil.Error:

    # print info to user
    print ("\n\nFile with the same name as newly generated xml already exist on %s." % apv.folder09)
    print ("Rename the file first before executing this program.\n")
    # exit from the program
    exit()

else:

    # print info to user
    print ("\nHaar Cascade classifier parser train ended.\n")