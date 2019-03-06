# pixhawk connection                    # parameter to connect raspberry pi with pixhawk
connection = "/dev/ttyS0"               # when connecting to pixhawk via serial connection
timeout = 30                            # how long in second dronekit should keep reconnect
baud = 57600                            # baudrate for communicating with pixhawk

# transmission control protocol         # setting for tcp connection
pc = "192.168.2.105"                    # computer ip address
rpi = "192.168.2.107"                   # raspberry pi ip address
video = 8000                            # video port
rangefinder = 8002                      # rangefinder port
controller = 8004                       # client port

# raspberry pi camera module            # camera module setting
x = 320                                 # camera x-axis size
y = 240                                 # camera y-axis size
fps = 30                                # camera frame per second

# rangefinder distance soft limit       # rangefinder setting
truncate = 50                          # limit distance to be measured by rangefinder to 0.5 [m]

# controller override channel 1         # futaba controller raw input [left and right]
left = 1154                             # channel 1 reading when rover steering turns left
right = 1874                            # channel 1 reading when rover steering turns right
center = 1532                           # channel 1 reading when rover steering is center
mleft = 1104                            # channel 1 reading when rover steering turns full left
mright = 1924                           # channel 1 reading when rover steering turns full right

# controller override channel 3         # futaba controller raw input [forward and backward]
stop = 1515                             # channel 3 reading when rover brake
forward = 1640                          # channel 3 reading when rover move forward
backward = 1410                         # channel 3 reading when rover move backward
mforward = 1924                         # channel 3 reading when rover move full forward
mbackward = 1104                        # channel 3 reading when rover move full backward