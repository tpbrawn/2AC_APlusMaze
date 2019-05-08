############################################################################
###########################  4WayShape.py  #################################
############################################################################
############################################################################
#This program shines the LEDs at the 4 response ports and awaits
#response via breaking beam at IR detectors. When a response is detected
#at any of the ports, a liquid reward is given via syringe pump at that
#reward location

############################################################################
#run concurrently with arduino files:
#       -Shape01_4-PortTrials.ino at each arduino
############################################################################


############################################################################
#########################   import libraries   #############################
############################################################################
import serial
import time
import datetime
import os
import sys
import random
import subprocess
import argparse

############################################################################
######################   initialize variables   ############################
############################################################################
subjectID = "999"               #default ID; need to overwrite in command line
trialNum = 1                    #initialize trial number
maxTrialsNorth = 3              #maximum number of trials to run at North port
maxTrialsEast = 3               #maximum number of trials to run at East port
maxTrialsSouth = 3              #maximum number of trials to run at South port
maxTrialsWest = 3               #maximum number of trials to run at West port
maxTrials = maxTrialsNorth+maxTrialsEast+maxTrialsSouth+maxTrialsWest   #maximum number of trials to run
numTrialsNorth = 0
numTrialsEast = 0
numTrialsSouth = 0
numTrialsWest = 0
#beamBreakStim = "RewardAudStim_880Hz_p1s.wav"

############################################################################
######################   initialize speakers   #############################
############################################################################
#speaker name changes sometimes on reboots or usb disconnections; need to check speaker
#names with "pactl list short sinks" command

#SpeakerNorth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo"
#SpeakerEast = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.2"
#SpeakerSouth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.3"
#SpeakerWest = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.4"

#SpeakerNorth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo"
#SpeakerEast = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.2"
#SpeakerSouth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.3"
#SpeakerWest = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.4"

############################################################################
###########   set up serial communication with arduino   ###################
############################################################################
#usb arduino ports on linux:
usbPortNorth = "/dev/ttyACM3"
usbPortEast = "/dev/ttyACM4"
usbPortSouth = "/dev/ttyACM5"
usbPortWest = "/dev/ttyACM6"

#usb  arduino ports on mac
#usbPortNorth = "/dev/tty.usbmodem14111"
#usbPortEast = "/dev/tty.usbmodem14121"
#usbPortSouth = "/dev/tty.usbmodem14131"
#usbPortWest = "/dev/tty.usbmodem14141"

#start serial communication
baudRate = 9600
serialTimeout = 0.005   #timeout is needed; 0.005 works
serNorth = serial.Serial(usbPortNorth, baudRate, timeout=serialTimeout)
serEast = serial.Serial(usbPortEast, baudRate, timeout=serialTimeout)
serSouth = serial.Serial(usbPortSouth, baudRate, timeout=serialTimeout)
serWest = serial.Serial(usbPortWest, baudRate, timeout=serialTimeout)

############################################################################
######################   parse command line  ###############################
############################################################################
parser = argparse.ArgumentParser()
parser.add_argument("--SID", help="set subject ID")
parser.add_argument("--Num", help="set daily procedure number")
args = parser.parse_args()

if args.SID:
    subjectID = args.SID
else:
    print("subject ID required: e.g., --SID 001")
    raise SystemExit

if args.Num:
    procedureNumber = args.Num
else:
    print ("procedure number required: e.g., --Num 01")
    raise SystemExit

############################################################################
#####################   initialize data file   #############################
############################################################################

#get start time and date for training session
trainingProtocolStartTime = str(datetime.datetime.now()).split(' ')
startTimePrecise = trainingProtocolStartTime[1]
startTime = startTimePrecise[0:8]
startDate = trainingProtocolStartTime[0]
fname_StartDate_pt1 = startDate[5:7]
fname_StartDate_pt2 = startDate[8:10]
fname_StartDate_pt3 = startDate[2:4]
fname_StartDate = fname_StartDate_pt1+fname_StartDate_pt2+fname_StartDate_pt3

trainingProtocol = "Shape01_4PortTrials"
filename = subjectID + "_" + trainingProtocol + "_TrialData_" +fname_StartDate + "-" + procedureNumber + ".txt"

if os.path.isfile(filename):                    #check if filename exists and exit to avoid overwriting
    print "\nFilename already exits. Exiting\n"
    raise SystemExit
else:
    print "New file will be created: " + filename

trialData = open(filename, 'w')
trialData.write("Filename: %s\n" %filename)
trialData.write("Subject ID: %s\n" %subjectID)
trialData.write("Start Date: %s\n" %startDate)
trialData.write("Start Time: %s\n" %startTime)
trialData.write("Training Protocol: %s\n\n" %trainingProtocol)
trialData.write("Trial#\tRespPort     Time          Date\n")
trialData.write("******\t********  ***********   **********\n")

############################################################################
############################   Trial Code   ################################
############################################################################
print "Initiating Training Protocol", trainingProtocol

##### Begin trial loop #####
while trialNum <= maxTrials:
    #check each IR-Detector for beam break
    irNorth = serNorth.readline()
    irEast = serEast.readline()
    irSouth = serSouth.readline()
    irWest = serWest.readline()

    if (len(irNorth) == 8) or (len(irEast) == 8) or (len(irSouth) == 8) or (len(irWest) == 8):
        #trial data for output file
        trialResponseTime = datetime.datetime.now()
        trialResponseTimeSplit = str(datetime.datetime.now()).split(' ')
        responseTimePrecise = trialResponseTimeSplit[1]
        responseTime = responseTimePrecise[0:11]
        responseDate = trialResponseTimeSplit[0]

        if (len(irNorth) == 8):                          #length of "broken\n" (from arduino code)
            #subprocess.call(SpeakerNorth, shell=True)   #alternate: subprocess.call("pacmd set-default-sink 1", shell=True)
            portResponse = 'N'
            print "\n\nBeam Break Detected at North Port"
            trialResult = 1
            numTrialsNorth = numTrialsNorth+1
        elif (len(irEast) == 8):
            #subprocess.call(SpeakerEast, shell=True)
            portResponse = 'E'
            print "\n\nBeam Break Detected at East Port"
            trialResult = 1
            time.sleep(.5)
            numTrialsEast = numTrialsEast+1
        elif (len(irSouth) == 8):
            #subprocess.call(SpeakerSouth, shell=True)
            portResponse = 'S'
            print "\n\nBeam Break Detected at South Port"
            trialResult = 1
            numTrialsSouth = numTrialsSouth+1
        elif (len(irWest) == 8):
            #subprocess.call(SpeakerWest, shell=True)
            portResponse = 'W'
            print "\n\nBeam Break Detected at West Port"
            trialResult = 1
            numTrialsWest = numTrialsWest+1
        #subprocess.call(["aplay", beamBreakStim])
        #subprocess.call(["aplay", beamBreakStim])

        #add to trial data file
        trialData.write("  %d\t   %s\t  %s   %s\n" %(trialNum, portResponse, responseTime, responseDate))
        trialData.flush()       #write to data file before closing; updates with each trial
        trialNum += 1

    if numTrialsNorth == maxTrialsNorth:
        serNorth.write('X')
    if numTrialsEast == maxTrialsEast:
        serEast.write('X')
    if numTrialsSouth == maxTrialsSouth:
        serSouth.write('X')
    if numTrialsWest == maxTrialsWest:
        serWest.write('X')

trialData.close()
time.sleep(40)      #wait until last port finishes 30s delay (from arduino) to shut off port

exit_index = 1
while exit_index < 5:
    serNorth.write('X')
    serEast.write('X')
    serSouth.write('X')
    serWest.write('X')
    time.sleep(1)
    exit_index = exit_index+1
print "Exiting", trainingProtocol
raise SystemExit
