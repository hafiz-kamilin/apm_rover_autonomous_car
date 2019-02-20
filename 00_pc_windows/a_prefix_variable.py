# transmission control protocol         # setting for tcp connection
pc = "192.168.2.105"                    # computer ip address
rpi = "192.168.2.107"                   # raspberry pi ip address
video = 8000                            # video port
rangefinder = 8002                      # rangefinder port
controller = 8004                       # client port

# folder and file naming                # specify permanent file and folder naming
file00 = "label_array.npz"              # npz file naming
folder00 = "01_training_data"           # saved steer data folder naming
folder01 = "00_original_image"          # saved steer data folder01 naming
folder02 = "01_filtered_image"          # saved steer data folder02 naming
folder03 = "02_steer_datasets"          # doubled steer data folder naming
folder04 = "03_keras_model_h5"          # saved trained keras tf model weight naming
folder05 = "04_cascade_datasets"        # saved object image to train haar cascade classifier
folder06 = "00_template_object"         # object picture template that need to be detected
folder07 = "01_negative_object"         # negative image training for haar cascade classifier
folder08 = "02_positive_object"         # positive image training for haar cascade classifier
folder09 = "05_haar_cascade_xml"        # saved trained haar cascade classifier
folder10 = "06_autonomous_result"       # saved self driving image result

# temp folder and file naming           # specify temporary file and folder naming
tempfile00 = "TEMP_label_array.npz"     # specify temporary file naming
tempfolder00 = "TEMP_original_image"    # temporary saved data folder01 naming
tempfolder01 = "TEMP_filtered_image"    # temporary saved data folder02 naming
tempfolder02 = "TEMP_model_epoch"       # temporary saved data folder04 naming
tempfolder03 = "TEMP_model_round"       # temporary saved data folder04 naming
tempfolder04 = "TEMP_xml_round"         # temporary saved data folder05 naming

# image processing                      # edge canny parameter
sigma = 0.75                            # intensity for edge canny filtering

# classifier                            # object recognition classifier
stop = "stop.xml"                       # stop 止
move = "move.xml"                       # move 動