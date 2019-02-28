############################################################################
############################   4WayShape_1Port.py  #########################
############################################################################
#This program shines one of the four LEDs (north, east, south, west) and
#waits for response via beam break of associated IR detector. Upon response,
#reward is given from syringe pump and one of the other ports randomly shines
#again and awaits response via the associated IR detector.
############################################################################
#run concurrently with arduino files:
#       -Shape02_1-PortTrials_North.ino
#       -Shape02_1-PortTrials_East.ino
#       -Shape02_1-PortTrials_South.ino
#       -Shape02_1-PortTrials_West.ino

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
trialNum = 1                                    #initialize trial number
maxTrialNum = 99                                #maximum number of trials to run
rewardStim = "RewardAudStim_880Hz_p1s.wav"

############################################################################
######################   initialize speakers   ############################
############################################################################
#speaker name changes sometimes on reboots or usb disconnections;
#need to check speaker names with "pactl list short sinks" command

SpeakerNorth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo"
SpeakerEast = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.2"
SpeakerSouth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.3"
SpeakerWest = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.4"

#SpeakerNorth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo"
#SpeakerEast = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.2"
#SpeakerSouth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.3"
#SpeakerWest = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo"

############################################################################
###########   set up serial communication with arduino   ###################
############################################################################
#usb arduino ports on linux:
usbPortNorth = "/dev/ttyACM0"
usbPortEast = "/dev/ttyACM1"
usbPortSouth = "/dev/ttyACM2"
usbPortWest = "/dev/ttyACM3"

#usb  arduino ports on mac
#usbPortNorth = "/dev/tty.usbmodem14111"
#usbPortEast = "/dev/tty.usbmodem14121"
#usbPortSouth = "/dev/tty.usbmodem14131"
#usbPortWest = "/dev/tty.usbmodem14141"

#start serial communication
baudRate = 9600
serialTimeout = 0.005        #timeout is needed; 0.005 works
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

trainingProtocol = "Shape02_1-PortTrials"
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

#Pick initial trial initiation port location:
randomPort = random.randint(1,4)
if randomPort == 1:
    portLocation = 'N'
elif randomPort == 2:
    portLocation = 'E'
elif randomPort == 3:
    portLocation = 'S'
else:
    portLocation = 'W'
print "\nNext Port Location: %s" %portLocation

############################
##### Begin trial loop #####
############################
while trialNum <= maxTrialNum:

##################################################################
#######################    North Port     ########################
##################################################################
    if portLocation == 'N':
        while True:
            serNorth.write(portLocation)
            time.sleep(0.02)
            serSouth.write(portLocation)
            time.sleep(0.02)
            serEast.write(portLocation)
            time.sleep(0.02)
            serWest.write(portLocation)
            time.sleep(0.02)
            irDetectorState = serNorth.readline()
            #print irDetectorState

            #if beam break detected
            if len(irDetectorState) == 8:                       #length of "broken\n" (from arduino code)
                subprocess.call(SpeakerNorth, shell=True)       #switch to north speaker
                #time.sleep(0.02)
                portResponse = 'N'
                print "Beam Break Detected at North Port"
            #    subprocess.call(["aplay", rewardStim])          #use aplay for linux, afplay for mac
            #    subprocess.call(["aplay", rewardStim])

                #Get time of trial response
                trialResponseTime = str(datetime.datetime.now()).split(' ')
                trialResponseTimePrecise = trialResponseTime[1]
                responseTime = trialResponseTimePrecise[0:11]
                responseDate = trialResponseTime[0]



                #Pick next trial port location that is different from current port
                randomPort = random.randint(1,3)
                if randomPort == 1:
                    portLocation = 'E'
                elif randomPort == 2:
                    portLocation = 'S'
                elif randomPort == 3:
                    portLocation = 'W'
                print "\n\nNext Port Location: %s" %portLocation
                break
##################################################################
#######################  End North Port     ######################
##################################################################

##################################################################
#######################    East Port     #########################
##################################################################
    elif portLocation == 'E':
        while True:
            serNorth.write(portLocation)
            time.sleep(0.02)
            serSouth.write(portLocation)
            time.sleep(0.02)
            serEast.write(portLocation)
            time.sleep(0.02)
            serWest.write(portLocation)
            time.sleep(0.02)
            irDetectorState = serEast.readline()
            #print irDetectorState

            #if beam break detected
            if len(irDetectorState) == 8:                       #length of "broken\n" (from arduino code)
                subprocess.call(SpeakerEast, shell=True)        #switch to east speaker
                #time.sleep(0.02)
                portResponse = 'E'
                print "Beam Break Detected at East Port"
                #subprocess.call(["aplay", rewardStim])          #use aplay for linux, afplay for mac
                #subprocess.call(["aplay", rewardStim])

                #Get time of trial initiation
                trialResponseTime = str(datetime.datetime.now()).split(' ')
                trialResponseTimePrecise = trialResponseTime[1]
                responseTime = trialResponseTimePrecise[0:11]
                responseDate = trialResponseTime[0]



                #Pick next trial port location that is different form current [prt]:
                randomPort = random.randint(1,3)
                if randomPort == 1:
                    portLocation = 'N'
                elif randomPort == 2:
                    portLocation = 'S'
                elif randomPort == 3:
                    portLocation = 'W'
                print "\n\nNext Port Location: %s" %portLocation
                break
##################################################################
#######################  End East Port     #######################
##################################################################

##################################################################
#######################    South Port     ########################
##################################################################
    elif portLocation == 'S':
        while True:
            serNorth.write(portLocation)
            time.sleep(0.02)
            serSouth.write(portLocation)
            time.sleep(0.02)
            serEast.write(portLocation)
            time.sleep(0.02)
            serWest.write(portLocation)
            time.sleep(0.02)
            irDetectorState = serSouth.readline()
            #print irDetectorState

            #if beam break detected
            if len(irDetectorState) == 8:                       #length of "broken\n" (from arduino code)
                subprocess.call(SpeakerSouth, shell=True)       #switch to south speaker
                #time.sleep(0.02)
                portResponse = 'S'
                print "Beam Break Detected at South Port"
            #    subprocess.call(["aplay", rewardStim])          #use aplay for linux, afplay for mac
            #    subprocess.call(["aplay", rewardStim])

                #Get time of trial initiation
                trialResponseTime = str(datetime.datetime.now()).split(' ')
                trialResponseTimePrecise = trialResponseTime[1]
                responseTime = trialResponseTimePrecise[0:11]
                responseDate = trialResponseTime[0]

                #Pick next trial port location that is different from current port:
                randomPort = random.randint(1,3)
                if randomPort == 1:
                    portLocation = 'N'
                elif randomPort == 2:
                    portLocation = "E"
                elif randomPort == 3:
                    portLocation = "W"
                print "\n\nNext Port Location: %s" %portLocation
                break
##################################################################
#######################  End South Port     ######################
##################################################################

##################################################################
#######################    West Port     #########################
##################################################################
    elif portLocation == 'W':
        while True:
            serNorth.write(portLocation)
            time.sleep(0.02)
            serSouth.write(portLocation)
            time.sleep(0.02)
            serEast.write(portLocation)
            time.sleep(0.02)
            serWest.write(portLocation)
            time.sleep(0.02)
            irDetectorState = serWest.readline()
            #print irDetectorState

            #if beam break detected
            if len(irDetectorState) == 8:                       #length of "broken\n" (from arduino code)
                subprocess.call(SpeakerWest, shell=True)        #switch to west speaker
                time.sleep(0.02)
                portResponse = 'W'
                print "Beam Break Detected at West Port"
            #    subprocess.call(["aplay", rewardStim])          #use aplay for linux, afplay for mac
            #    subprocess.call(["aplay", rewardStim])

                #Get time of trial initiation
                trialResponseTime = str(datetime.datetime.now()).split(' ')
                trialResponseTimePrecise = trialResponseTime[1]
                responseTime = trialResponseTimePrecise[0:11]
                responseDate = trialResponseTime[0]

                #Pick next trial port location that is different from current port:
                randomPort = random.randint(1,3)
                if randomPort == 1:
                    portLocation = 'N'
                elif randomPort == 2:
                    portLocation = "E"
                elif randomPort == 3:
                    portLocation = "S"
                print "\n\nNext Port Location: %s" %portLocation
                break
##################################################################
#######################  End West Port     #######################
##################################################################

    #Write trial data
    trialData.write("  %d\t   %s\t  %s   %s\n" %(trialNum, portResponse, responseTime, responseDate))
    trialData.flush()  #write to data file before closing; updates with each trial
    trialNum += 1

##########################
##### Exit Procedure #####
##########################
time.sleep(1)
trialData.close()
exit_index = 1
while exit_index < 5:
    serNorth.write('X')
    time.sleep(.2)
    serEast.write('X')
    time.sleep(.2)
    serSouth.write('X')
    time.sleep(.2)
    serWest.write('X')
    time.sleep(.2)
    exit_index = exit_index+1
    time.sleep(.2)
print "Exiting", trainingProtocol
raise SystemExit
