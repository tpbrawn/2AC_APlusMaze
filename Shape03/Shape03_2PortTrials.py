############################################################################
############################   Shape03_2PortTrials.py  #####################
############################################################################
#This program shines one of two LEDs (north or south) and waits for
#response via beam break of associated IR detector. Upon response, the East
#or West LED flashes and awaits response via the associated IR detector.
#Upon response, the associated step motor is moved to dispense liquid reward
#from syringe pump

#Shape03 is identical to Shape04 except Shape04 does not reward responses
#to North and South portsself.

#To train rats to initiate trials at North/South port and respond at
#East/West port, begin with equal reward at N/S and E/W ports. As rat
#progresses, decrease the N/S reward and increase (or leave as is) the
#E/W reward until rat is successful with no reward at N/S ports.

############################################################################
#run concurrently with arduino files:
#       -Shape03_2PortTrials_North.ino
#       -Shape03_2PortTrials_East.ino
#       -Shape03_2PortTrials_South.ino
#       -Shape03_2PortTrials_West.ino

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
#####################   define function: InitPortSelect  ###################
############################################################################
def InitPortSelect():
    if random.randint(1,2) == 1:
        initPortLocation = 'N'
    else:
        initPortLocation = 'S'
    print "\nNext Port Location: %s" %initPortLocation
    return(initPortLocation)

############################################################################
#####################   define function: RespPortSelect  ###################
############################################################################
def RespPortSelect():
    if random.randint(1,2) == 1:
        respPortLocation = 'E'
        print "\n\nNext Port Location: %s" %respPortLocation
    else:
        respPortLocation = 'W'
        print "\n\nNext Port Location: %s" %respPortLocation
    return(respPortLocation)

############################################################################
################   define function: SendInitPortSignal   ###################
############################################################################
def SendInitPortSignal(initPortLocation):
    serNorth.write(initPortLocation)
    time.sleep(0.02)
    serSouth.write(initPortLocation)
    time.sleep(0.02)
    serEast.write(initPortLocation)
    time.sleep(0.02)
    serWest.write(initPortLocation)
    time.sleep(0.02)

############################################################################
################   define function: SendRespPortSignal   ###################
############################################################################
def SendRespPortSignal(respPortLocation):
    serNorth.write(respPortLocation)
    time.sleep(0.02)
    serSouth.write(respPortLocation)
    time.sleep(0.02)
    serEast.write(respPortLocation)
    time.sleep(0.02)
    serWest.write(respPortLocation)
    time.sleep(0.02)

############################################################################
###############   define function: InterTrialCountdown   ###################
############################################################################
def InterTrialCountdown(interTrialDuration):
    print "%d Seconds til next trial\n\n" %interTrialDuration
    while (interTrialDuration > 0):
        serEast.write('Z')
        serWest.write('Z')
        time.sleep(1)
        interTrialDuration = interTrialDuration-1

############################################################################
######################   initialize variables   ############################
############################################################################
trialNum = 1                                        #initialize trial number
completedTrialNum = 0                               #initialize number of completed trials
maxCompletedTrialNum = 20                           #maximum number of trials to run
subjectID = "999"                                   #default ID; need to overwrite in command line
responseWindow = 30                                 #duration (in seconds) to wait for response at east/west port after north/south trial initation
interTrialDuration_Response = 5
interTrialDuration_NoResponse = 15
#beamBreakStim = "RewardAudStim_880Hz_p1s.wav"
#noResponseStim = "Brawn_ErrorStim_WhiteNoise.wav"

############################################################################
######################   initialize speakers   #############################
############################################################################
#speaker name changes sometimes on reboots or usb disconnections;
#need to check speaker names with "pactl list short sinks" command

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

#usb arduino ports on mac
#usbPortNorth = "/dev/tty.usbmodem14111"
#usbPortEast = "/dev/tty.usbmodem14121"
#usbPortSouth = "/dev/tty.usbmodem14131"
#usbPortWest = "/dev/tty.usbmodem14141"

#start serial communication
baudRate = 9600
serialTimeout = 0.005       #timeout is needed; 0.005 works
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

trainingProtocol = "Shape03_2PortTrials"
filename = subjectID + "_" + trainingProtocol + "_TrialData_" +fname_StartDate + "-" + procedureNumber + ".txt"
if os.path.isfile(filename):                    #check if filename exists and exit to avoid overwriting
    print "\n\nFilename already exits. Exiting\n"
    raise SystemExit
else:
    print "\nNew file will be created: " + filename
trialData = open(filename, 'w')
trialData.write("Filename: %s\n" %filename)
trialData.write("Subject ID: %s\n" %subjectID)
trialData.write("Start Date: %s\n" %startDate)
trialData.write("Start Time: %s\n" %startTime)
trialData.write("Training Protocol: %s\n\n\n"  %trainingProtocol)
trialData.write("Trial#\tInitPort   InitTime\tRespPort   RespTime\t   Date\n")
trialData.write("******\t********  ***********\t********  ***********\t**********\n")

############################################################################
############################   Trial Code   ################################
############################################################################
print "Initiating Training Protocol", trainingProtocol

#Pick initial trial initiation port location:
initPortLocation = InitPortSelect()

############################
##### Begin trial loop #####
############################
while completedTrialNum < maxCompletedTrialNum:

    ###########################################################################
    #######################    North Port Initiate     ########################
    ###########################################################################
    if initPortLocation == 'N':
        SendInitPortSignal(initPortLocation)
        irDetectorState = serNorth.readline()
        #print irDetectorState

        #if beam break detected
        if len(irDetectorState) == 8:                               #length of "broken\n" (from arduino code)
            #subprocess.call(SpeakerNorth, shell=True)               #switch to North Speaker
            print "Beam Break Detected at North Port"
            trialInitTime = str(datetime.datetime.now()).split(' ') #Get time of trial initiation
            trialInitTimePrecise = trialInitTime[1]
            initTime = trialInitTimePrecise[0:8]
            initDate = initTime[0]
            #subprocess.call(["aplay", beamBreakStim])
            #subprocess.call(["aplay", beamBreakStim])
            trialHalfTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow/2)
            trialHalfTimeSignal = 0
            trialEndTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow)

            #pick next resposne port location
            respPortLocation = RespPortSelect()

            ####################################################################
            #####################    East Port Response    #####################
            ####################################################################
            if respPortLocation == 'E':
                while True:
                    SendRespPortSignal(respPortLocation)
                    irDetectorState = serEast.readline()
                    #print irDetectorState

                    #if beam break detected at East Port
                    if len(irDetectorState) == 8:                                   #length of "broken\n" (from arduino code)
                        #subprocess.call(SpeakerEast, shell=True)                    #switch to east speaker
                        print "Beam Break Detected at East Port"
                        trialResponseTime = str(datetime.datetime.now()).split(' ') #Get time of response
                        responseTimePrecise = trialResponseTime[1]
                        responseTime = responseTimePrecise[0:8]
                        responseDate = trialResponseTime[0]
                        #subprocess.call(["aplay", beamBreakStim])
                        #subprocess.call(["aplay", beamBreakStim])

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t  %s\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()           #write to data file before closing; updates with each trial
                        trialNum += 1               #increment trial number
                        completedTrialNum += 1      #increment number of completed trials

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_Response)

                        #pick next init port location
                        initPortLocation = InitPortSelect()
                        break

                    ##################################################
                    ##### end trial if no response during window #####
                    ##################################################
                    elif (datetime.datetime.now() >= trialHalfTime) and (datetime.datetime.now() < trialEndTime) :
                        if trialHalfTimeSignal == 0:
                            #subprocess.call(["aplay", noResponseStim])
                            trialHalfTimeSignal = 1
                    elif datetime.datetime.now() >= trialEndTime:
                        respPortLocation = 'E'
                        responseDate = 'X'
                        responseTime = 'X'

                        #send signals to cancel east or west port
                        SendInitPortSignal(initPortLocation)

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t       %s\t\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number

                        time.sleep(3)           #gives time for port to turn off before sound plays
                        #subprocess.call(["aplay", noResponseStim])
                        #subprocess.call(["aplay", noResponseStim])

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_NoResponse)

                        #pick next init port location
                        initPortLocation = InitPortSelect()

                        break

            ####################################################################
            #####################    West Port Response    #####################
            ####################################################################
            if respPortLocation == 'W':
                while True:
                    SendRespPortSignal(respPortLocation)
                    irDetectorState = serWest.readline()
                    #print irDetectorState

                    #if beam break detected at West Port
                    if len(irDetectorState) == 8:                                   #length of "broken\n" (from arduino code)
                        #subprocess.call(SpeakerWest, shell=True)                    #switch to west speaker
                        print "Beam Break Detected at West Port"
                        trialResponseTime = str(datetime.datetime.now()).split(' ') #Get time of response
                        responseTimePrecise = trialResponseTime[1]
                        responseTime = responseTimePrecise[0:8]
                        responseDate = trialResponseTime[0]
                        #subprocess.call(["aplay", beamBreakStim])
                        #subprocess.call(["aplay", beamBreakStim])

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t  %s\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number
                        completedTrialNum += 1  #increment number of completed trials

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_Response)

                        #pick next init port location
                        initPortLocation = InitPortSelect()
                        break

                    ##################################################
                    ##### end trial if no response during window #####
                    ##################################################
                    elif (datetime.datetime.now() >= trialHalfTime) and (datetime.datetime.now() < trialEndTime) :
                        if trialHalfTimeSignal == 0:
                            #subprocess.call(["aplay", noResponseStim])
                            trialHalfTimeSignal = 1
                    elif datetime.datetime.now() >= trialEndTime:
                        respPortLocation = 'W'
                        responseDate = 'X'
                        responseTime = 'X'

                        #send signals to cancel east or west port
                        SendInitPortSignal(initPortLocation)


                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t       %s\t\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number

                        time.sleep(3)           #gives time for port to turn off before sound plays
                        #subprocess.call(["aplay", noResponseStim])
                        #subprocess.call(["aplay", noResponseStim])

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_NoResponse)

                        #pick next init port location
                        initPortLocation = InitPortSelect()

                        break

    ###########################################################################
    #######################    South Port Initiate     ########################
    ###########################################################################
    if initPortLocation == 'S':
        SendInitPortSignal(initPortLocation)
        irDetectorState = serSouth.readline()
        #print irDetectorState

        #if beam break detected
        if len(irDetectorState) == 8:                                   #length of "broken\n" (from arduino code)
            #subprocess.call(SpeakerSouth, shell=True)                   #switch to south speaker
            print "Beam Break Detected at South Port"
            trialInitTime = str(datetime.datetime.now()).split(' ')     #Get time of trial initiation
            trialInitTimePrecise = trialInitTime[1]
            initTime = trialInitTimePrecise[0:8]
            initDate = initTime[0]
            #subprocess.call(["aplay", beamBreakStim])
            #subprocess.call(["aplay", beamBreakStim])
            trialHalfTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow/2)
            trialHalfTimeSignal = 0
            trialEndTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow)

            #pick next response port location
            respPortLocation = RespPortSelect()

            ####################################################################
            #####################    East Port Response    #####################
            ####################################################################
            if respPortLocation == 'E':
                while True:
                    SendRespPortSignal(respPortLocation)
                    irDetectorState = serEast.readline()
                    #print irDetectorState

                    #if beam break detected at East Port
                    if len(irDetectorState) == 8:                                   #length of "broken\n" (from arduino code)
                        #subprocess.call(SpeakerEast, shell=True)                    #swich to east speaker
                        print "Beam Break Detected at East Port"
                        trialResponseTime = str(datetime.datetime.now()).split(' ') #Get time of response
                        responseTimePrecise = trialResponseTime[1]
                        responseTime = responseTimePrecise[0:8]
                        responseDate = trialResponseTime[0]
                        #subprocess.call(["aplay", beamBreakStim])
                        #subprocess.call(["aplay", beamBreakStim])

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t  %s\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number
                        completedTrialNum += 1  #increment number of completed trials

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_Response)

                        #pick next init port location
                        initPortLocation = InitPortSelect()

                        break

                    ##################################################
                    ##### end trial if no response during window #####
                    ##################################################
                    elif (datetime.datetime.now() >= trialHalfTime) and (datetime.datetime.now() < trialEndTime) :
                        if trialHalfTimeSignal == 0:
                            #subprocess.call(["aplay", noResponseStim])
                            trialHalfTimeSignal = 1
                    elif datetime.datetime.now() >= trialEndTime:
                        respPortLocation = 'E'
                        responseDate = 'X'
                        responseTime = 'X'

                        #send signals to cancel east or west port
                        SendInitPortSignal(initPortLocation)

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t       %s\t\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number

                        time.sleep(3)           #gives time for port to turn off before sound plays
                        #subprocess.call(["aplay", noResponseStim])
                        #subprocess.call(["aplay", noResponseStim])

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_NoResponse)

                        #pick next init port location
                        initPortLocation = InitPortSelect()

                        break

            ####################################################################
            #####################    West Port Response    #####################
            ####################################################################
            if respPortLocation == 'W':
                while True:
                    SendRespPortSignal(respPortLocation)
                    irDetectorState = serWest.readline()
                    #print irDetectorState

                    #if beam break detected at West Port
                    if len(irDetectorState) == 8:   #length of "broken\n" (from arduino code)
                    #    subprocess.call(SpeakerWest, shell=True)                    #switch to west speaker
                        print "Beam Break Detected at West Port"
                        trialResponseTime = str(datetime.datetime.now()).split(' ') #Get time of response
                        responseTimePrecise = trialResponseTime[1]
                        responseTime = responseTimePrecise[0:8]
                        responseDate = trialResponseTime[0]
                        #subprocess.call(["aplay", beamBreakStim])
                        #subprocess.call(["aplay", beamBreakStim])

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t  %s\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number
                        completedTrialNum += 1  #increment number of completed trials

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_Response)

                        #pick next init port location
                        initPortLocation = InitPortSelect()

                        break

                    ##################################################
                    ##### end trial if no response during window #####
                    ##################################################
                    elif (datetime.datetime.now() >= trialHalfTime) and (datetime.datetime.now() < trialEndTime) :
                        if trialHalfTimeSignal == 0:
                            #subprocess.call(["aplay", noResponseStim])
                            trialHalfTimeSignal = 1
                    elif datetime.datetime.now() >= trialEndTime:
                        respPortLocation = 'W'
                        responseDate = 'X'
                        responseTime = 'X'

                        #send signals to cancel east or west port
                        SendInitPortSignal(initPortLocation)

                        #add to trial data file
                        trialData.write("  %d\t   %s\t  %s\t   %s\t       %s\t\t%s\n" %(trialNum, initPortLocation, initTime, respPortLocation, responseTime, responseDate))
                        trialData.flush()       #write to data file before closing; updates with each trial
                        trialNum += 1           #increment trial number

                        time.sleep(3)           #gives time for port to turn off before sound plays
                        #subprocess.call(["aplay", noResponseStim])
                        #subprocess.call(["aplay", noResponseStim])

                        #Countdown til next trial
                        InterTrialCountdown(interTrialDuration_NoResponse)

                        #pick next init port location
                        initPortLocation = InitPortSelect()

                        break

############################################################################
###################   Exit Training Protocol   #############################
############################################################################
time.sleep(1)
trialData.write("\n%s is complete\n" %trainingProtocol)
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
print "Exiting", trainingProtocol
raise SystemExit
