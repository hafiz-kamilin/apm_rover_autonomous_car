#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules used in the program
import a_prefix_variable as apv
from numpy import load
import os

# if apv.folder02 doesn't exist end the program
if not os.path.exists(apv.folder00 + "/" + apv.folder02):

    print ("\nFolder /%s/%s/ where the .npz file supposedly located does not exist!\n" % (apv.folder00, apv.folder02))
    exit()

# if apv.folder03 doesn't exist end the program
if not os.path.exists(apv.folder03):

    print ("\nFolder /%s/ where the .npz file supposedly located does not exist!\n" % apv.folder03)
    exit()

# while loop
while True:

    try:

        # clear screen
        os.system("cls")
        # print out info for user
        print ("This program will open .npz file and print out the content")
        print ("in 2d array format understandable to the user.")
        print ("\nPick which .npz file you would like to open.")
        print ("[1] Original file.")
        print ("[2] Doubled file.")
        print ("[3] quit.")
        # get user input
        pick = int(input ("\nYour pick: "))

        # if pick is 1
        if (pick == 1):

            # load the apv.file00 into data
            data = load(apv.folder00 + "/" + apv.folder02 + "/" + apv.file00)
            # list the content inside the apv.file00
            lst = data.files
            # print the array legend
            print ("\n([LEFT. FORWARD. RIGHT.])")

            # for all the content exist inside the apv.file00
            for item in lst:
                
                # print out the content
                print(data[item])

            # break from while loop
            break

        # if pick is 2
        elif (pick == 2):

            # load the apv.file00 into data
            data = load(apv.folder03 + "/" + apv.file00)
            # list the content inside the apv.file00
            lst = data.files
            # print the array legend
            print ("\n([LEFT. FORWARD. RIGHT.])")

            # for all the content exist inside the apv.file00
            for item in lst:
                
                # print out the content
                print(data[item])

            # give some space here
            print ("\n")
            # break from while loop
            break

        # if pick is 3
        elif (pick == 3):

            # break from while loop
            break

    # if pick is not number
    except ValueError:

        # pass back to while loop
        pass

    # if file does't exist
    except FileNotFoundError:

        # print info to user
        print ("\nFile that need to be opened doesn't exist.\n")
        # break from while loop
        break

    # if pick number is out of range
    else:

        # pass back to while loop
        pass