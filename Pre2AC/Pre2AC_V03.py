############################################################################
##########################   Pre2AC_V03.py   ###############################
############################################################################
#This is the same code as 2AC_V03.py. It is run with Pre2AC arduino files
#so only the correct port is activeself.
#
#This program shines one of two LEDs (north or south) and waits for response
#via beam break of associated IR detector. Upon response, an auditory
#stimulus is played and the correct East or West LED shines and awaits response
#via the associated IR detectors. One sound indicates East response and one sound
#indicates West response. Upon correct response, the associated step motor is
#moved to produce liquid reward from the syringe pump and the same sound is
#played again from the response port speaker. Incorrect responses are not
#possible.

############################################################################
#run concurrently with arduino files:
#       -Pre2AC_North.ino
#       -Pre2AC_South.ino
#       -Pre2AC_East.ino
#       -Pre2AC_West.ino

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
################   define function: StimPortSelection   ####################
############################################################################
def StimPortSelection(trialResult, trialCorrections, initPortLocation, nextStim, respPortLocation, trialInitProcedure):

    #pick next init port location
    if (trialResult == 0) and (trialCorrections < maxTrialCorrections): #correction trial
        initPortLocation = initPortLocation
    else:
        if trialInitProcedure == 'N':
            initPortLocation = 'N'
        elif trialInitProcedure == 'S':
            initPortLocation = 'S'
        elif trialInitProcedure == 'B':
            if random.randint(1,2) == 1:     #north and south ports
                initPortLocation = 'N'
            else:
                initPortLocation = 'S'
    print "Next Port Location: %s" %initPortLocation

    #pick next stim to be played
    if (trialResult == 0) and (trialCorrections < maxTrialCorrections):  #correction trial
        nextstim = nextStim
        respPortLocation = respPortLocation
        trialCorrections = trialCorrections+1
        print "Next Stim: %s" %nextStim
    else:                                                               #non-correction trial
        if random.randint(1,2) == 1:
            nextStim = stimEast
            respPortLocation = 'E'
        else:
            nextStim = stimWest
            respPortLocation = 'W'
        trialCorrections=0
        print "Next Stim: %s" %nextStim
    return (initPortLocation, nextStim, respPortLocation, trialCorrections)

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
###############   define function: SendStimEastSignal   ####################
############################################################################
def SendStimEastSignal():
    # E = East response -> reward; W = West response -> no reward
    serEast.write('E')
    time.sleep(0.02)
    serWest.write('E')
    time.sleep(0.02)
    serNorth.write('Z')
    time.sleep(0.02)
    serSouth.write('Z')

############################################################################
################   define function: SendStimWestSignal   ###################
############################################################################
def SendStimWestSignal():
    # E = East response -> no reward; W = West response -> reward
    serEast.write('W')
    time.sleep(0.02)
    serWest.write('W')
    time.sleep(0.02)
    serNorth.write('Z')
    time.sleep(0.02)
    serSouth.write('Z')

############################################################################
##################   define function: TrialEvaluation   ####################
############################################################################
def TrialEvaluation(irEast, irWest, nextStim, initPortLocation):
    #compute trial result
    if (len(irEast) == 8) and (nextStim == stimEast):    #length of "broken\n" (from arduino code)
        portResponse = 'E'
        trialResult = 1
        time.sleep(.5)
        print "Beam Break Detected at %s" %portResponse
        subprocess.call(SpeakerEast, shell=True)
        rewardPlayback = 1
        while (rewardPlayback > 0):
            subprocess.call(["aplay", nextStim])
            time.sleep(1)
            rewardPlayback = rewardPlayback - 1
    elif (len(irEast) == 8) and (nextStim == stimWest):
        portResponse = 'E'
        trialResult = 0
        time.sleep(.5)
        print "Beam Break Detected at %s" %portResponse
        #subprocess.call(SpeakerWest, shell=True)
        subprocess.call(SpeakerEast, shell=True)
        errorPlayback = 2
        while (errorPlayback > 0):
            #subprocess.call(["aplay", nextStim])
            subprocess.call(["aplay", errorStim])
            time.sleep(.5)
            errorPlayback = errorPlayback - 1
        print  "%d second error delay" %errorDelay
        time.sleep(errorDelay)
    elif (len(irWest) == 8) and (nextStim == stimEast):
        portResponse = 'W'
        trialResult = 0
        time.sleep(.5)
        print "Beam Break Detected at %s" %portResponse
        subprocess.call(SpeakerWest, shell=True)
        #subprocess.call(SpeakerEast, shell=True)
        errorPlayback = 2
        while (errorPlayback > 0):
            #subprocess.call(["aplay", nextStim])
            subprocess.call(["aplay", errorStim])
            time.sleep(.5)
            errorPlayback = errorPlayback - 1
        print "%d second error delay" %errorDelay
        time.sleep(errorDelay)
    elif (len(irWest) == 8) and (nextStim == stimWest):
        portResponse = 'W'
        trialResult = 1
        time.sleep(.5)
        print "Beam Break Detected at %s" %portResponse
        subprocess.call(SpeakerWest, shell=True)
        rewardPlayback = 1
        while (rewardPlayback > 0):
            subprocess.call(["aplay", nextStim])
            time.sleep(1)
            rewardPlayback = rewardPlayback - 1

    #compute turn direction
    if (initPortLocation == 'N') and (portResponse == "E"):
        turnDirection = 'L'
    elif (initPortLocation == 'N') and (portResponse == "W"):
        turnDirection = 'R'
    elif (initPortLocation == 'S') and (portResponse == "E"):
        turnDirection = 'R'
    elif (initPortLocation == 'S') and (portResponse == "W"):
        turnDirection = 'L'

    return (portResponse, trialResult, turnDirection)

############################################################################
##############   define function: OutputTrialData_Response   ################
############################################################################
def OutputTrialData_Response(trialNum, respPortLocation, initPortLocation, portResponse, turnDirection, trialResult,\
 responseSpeed, initTime, responseTime, responseDate):
    if trialNum < 10 and responseSpeed < 10:
        trialData.write("%d       stim-%s       %s         %s         %s        %s        %d       %.2f    %s  %s  %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 10 and responseSpeed >= 10:
        trialData.write("%d       stim-%s       %s         %s         %s        %s        %d       %.2f   %s  %s  %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 100 and responseSpeed < 10:
        trialData.write("%d      stim-%s       %s         %s         %s        %s        %d       %.2f    %s  %s  %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 100 and responseSpeed >= 10:
        trialData.write("%d      stim-%s       %s         %s         %s        %s        %d       %.2f   %s  %s  %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 999 and responseSpeed < 10:
        trialData.write("%d     stim-%s       %s         %s         %s        %s        %d       %.2f    %s  %s  %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 999 and responseSpeed >= 10:
        trialData.write("%d     stim-%s       %s         %s         %s        %s        %d       %.2f   %s  %s  %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    trialData.flush()       #write to data file before closing; updates with each trial
    trialNum += 1           #increment trial number
    return (trialNum)

############################################################################
#############   define function: OutputTrialData_NoResponse   ###############
############################################################################
def OutputTrialData_NoResponse(trialNum, respPortLocation, initPortLocation, portResponse, turnDirection, trialResult,\
 responseSpeed, initTime, responseTime, responseDate):
    if trialNum < 10:
        trialData.write("%d       stim-%s       %s         %s         %s        %s        %s       %s       %s  %s         %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 100:
        trialData.write("%d      stim-%s       %s         %s         %s        %s        %s       %s       %s  %s         %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    elif trialNum < 999:
        trialData.write("%d     stim-%s       %s         %s         %s        %s       %s       %s       %s  %s         %s\n"\
         %(trialNum, respPortLocation, initPortLocation, respPortLocation, portResponse, turnDirection, trialResult,\
         responseSpeed, initTime, responseTime, responseDate))
    trialData.flush()       #write to data file before closing; updates with each trial
    trialNum += 1           #increment trial number
    return (trialNum)

############################################################################
#################   define function: AssignNoResponse   ####################
############################################################################
def AssignNoResponse():
    portResponse = 'X'
    trialResult = 'X'
    responseSpeed = 'X'
    responseTime = 'X'
    trialResult = 'X'
    responseDate = 'X'
    turnDirection = 'X'
    return(portResponse, trialResult, responseSpeed, responseTime, trialResult, responseDate, turnDirection)

############################################################################
######################   initialize variables   ############################
############################################################################
trialNum = 1                      #initialize trial number
trialResult = 999                 #initialize trial result; needed for intitial StimPortSelection
trialCorrections = 0              #initialize trial corrections
maxTrialNum = 200                 #maximum number of trials to run
responseWindow = 20               #duration (in seconds) to wait for response
errorDelay = 25                   #duration of added delay til next trial after error
responsePortDelay = 1          #duration (in seconds) before east/west ports turn on after stimulus playback
interTrialDuration_Response = 5
interTrialDuration_NoResponse = 15
initPortLocation = 'X'
nextStim = 'X'
respPortLocation = 'X'
#timeWarningStim = "WhiteNoise_p5s.wav"
#trialOverStim = "WhiteNoise_p5s.wav"
errorStim = "WhiteNoise_0p5s.wav"

############################################################################
######################   initialize speakers   ############################
############################################################################
#speaker name changes sometimes on reboots or usb disconnections;
#need to check speaker names with "pactl list short sinks" command

SpeakerNorth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.2"
#SpeakerEast = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.2"
#SpeakerSouth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.3"
SpeakerWest = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo.3"

#SpeakerNorth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo"
SpeakerEast = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo"
SpeakerSouth = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.2"
#SpeakerWest = "pacmd set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.iec958-stereo.2"

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
serialTimeout = 0.005       #timeout is needed; 0.005 works
serNorth = serial.Serial(usbPortNorth, baudRate, timeout=serialTimeout)
serEast = serial.Serial(usbPortEast, baudRate, timeout=serialTimeout)
serSouth = serial.Serial(usbPortSouth, baudRate, timeout=serialTimeout)
serWest = serial.Serial(usbPortWest, baudRate, timeout=serialTimeout)

############################################################################
######################   parse command line  ###############################
############################################################################
parser = argparse.ArgumentParser()
parser.add_argument("--SID", help="set subject ID: e.g., --SID 001")
parser.add_argument("--TIP", help="set trial initiation procedure: N = North, S = South, B = North and South")
parser.add_argument("--SpkrLoc", help="set procedure for location of stimulus playback: e.g., --SpkrLoc 4")
                    #    1 = all playbacks at Reward Port\n
                    #    2 = first playback at Initiation Port, second and third playback at Reward Port\n
                    #    3 = first and second playback at Initiation Port, third playback at Reward Port\n
                    #    4 = all playbacks at Initiation Port")
parser.add_argument("--MaxCor", help="set maximum number of consecutive correction trials: e.g., --MaxCor 1")
parser.add_argument("--SE", help="set stimulus-East: e.g., --SE upsweep.wav")
parser.add_argument("--SW", help="set stimulus-West: e.g., --SW downsweep.wav")
parser.add_argument("--ProcNum", help="set daily procedure number: e.g., --ProcNum 01")
args = parser.parse_args()

if args.SID:
    subjectID = args.SID
else:
    print("subject ID required: e.g., --SID 001")
    raise SystemExit

if args.TIP:
    trialInitProcedure = args.TIP
else:
    print("Trial Initiaton Procedure Required: e.g., --Init N")
    raise SystemExit

if args.SpkrLoc:
    speakerLocProcedure_string = args.SpkrLoc
    speakerLocProcedure = int(speakerLocProcedure_string)
else:
    print("Speaker Location Procedure required: e.g., --SpkrLoc 4")
    raise SystemExit

if args.MaxCor:
    maxTrialCorrections_string = args.MaxCor
    maxTrialCorrections = int(maxTrialCorrections_string)
else:
    print("max number of trial corrections required: e.g., --MaxCor 1")
    raise SystemExit

if args.SE:
    stimEast = args.SE
else:
    print("stimulus-East required: e.g., --SE upsweep.wav")
    raise SystemExit

if args.SW:
    stimWest = args.SW
else:
    print("stimulus-West required: e.g., --SW downsweep.wav")
    raise SystemExit

if args.ProcNum:
    procedureNumber = args.ProcNum
else:
    print ("procedure number required: e.g., --ProcNum 01")
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

trainingProtocol = "2AC"
filename = subjectID + "_" + trainingProtocol + "_TrialData_" + fname_StartDate + "-" + procedureNumber + ".txt"
if os.path.isfile(filename):                    #check if filename exists and exit to avoid overwriting
    print "\nFilename already exits. Exiting\n"
    raise SystemExit
else:
    print "New file will be created:" + filename
trialData = open(filename, 'w')
trialData.write("Filename: %s\n" %filename)
trialData.write("Subject ID: %s\n" %subjectID)
trialData.write("Start Date: %s\n" %startDate)
trialData.write("Start Time: %s\n" %startTime)
trialData.write("Training Protocol: %s\n"  %trainingProtocol)
trialData.write("Max Trial Corrections: %d\n" %maxTrialCorrections)
trialData.write("Stimuli:\n")
trialData.write("  -East stimulus: %s\n" %stimEast)
trialData.write("  -West stimulus: %s\n" %stimWest)
#trialData.write("  -Time Warning Stim: %s\n" %timeWarningStim)
#trialData.write("  -Trial Over Stim: %s\n" %trialOverStim)
trialData.write("  -Error Stim: %s\n\n\n" %errorStim)
trialData.write("Trial#  Stimulus  InitPort  RespPort  RespLoc  TurnDir  Result  RespSpeed  StimTime  RespTime     Date\n")
trialData.write("******  ********  ********  ********  *******  *******  ******  *********  ********  ********  **********\n")

############################################################################
############################   Trial Code   ################################
############################################################################
print "\nInitiating Training Protocol:", trainingProtocol, "\n"

#select initial port and stimulus
(initPortLocation, nextStim, respPortLocation, trialCorrections) =\
 StimPortSelection(trialResult, trialCorrections, initPortLocation, nextStim, respPortLocation, trialInitProcedure)

############################
##### Begin trial loop #####
############################
while trialNum <= maxTrialNum:

    ###########################################################################
    #######################    North Port Initiate     ########################
    ###########################################################################
    if initPortLocation == 'N':
        SendInitPortSignal(initPortLocation)
        irDetectorState = serNorth.readline()               #check north IR detector
        #print irDetectorState

        #if beam break detected
        if len(irDetectorState) == 8:                       #length of "broken\n" (from arduino code)
            print "Beam Break Detected at North Port"
            if speakerLocProcedure == 1:
                if nextStim == stimEast:
                    subprocess.call(SpeakerEast, shell=True)       #switch to east speaker
                elif nextStim == stimWest:
                    subprocess.call(SpeakerWest, shell=True)       #switch to west speaker
            elif speakerLocProcedure > 1:
                subprocess.call(SpeakerNorth, shell=True)       #switch to north speaker
            subprocess.call(["aplay", nextStim])
            time.sleep(1)
            if speakerLocProcedure == 1 or speakerLocProcedure == 2:
                if nextStim == stimEast:
                    subprocess.call(SpeakerEast, shell=True)       #switch to east speaker
                elif nextStim == stimWest:
                    subprocess.call(SpeakerWest, shell=True)       #switch to west speaker
            elif speakerLocProcedure > 2:
                subprocess.call(SpeakerNorth, shell=True)       #switch to north speaker
            #subprocess.call(["aplay", nextStim])
            trialStartTime = datetime.datetime.now()        #start trial time after preStimDelay
            trialInitTime = str(datetime.datetime.now()).split(' ')
            trialInitTimePrecise = trialInitTime[1]
            initTime = trialInitTimePrecise[0:8]
            initDate = trialInitTime[0]
            trialHalfTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow/2)
            trialHalfTimeSignal = 0
            trialEndTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow)
            print ".............................."
            time.sleep(responsePortDelay)

            while True:
                #send signals to arduino to shine East and West LEDs
                if nextStim == stimEast:
                    SendStimEastSignal()
                elif nextStim == stimWest:
                    SendStimWestSignal()

                #check east and west IR-Detectors
                irEast = serEast.readline()
                irWest = serWest.readline()

                #check for beam break at East and West IR-Detectors
                if (len(irEast) == 8) or (len(irWest) == 8):
                    trialResponseTime = datetime.datetime.now()
                    trialResponseTimeSplit = str(datetime.datetime.now()).split(' ')
                    responseTimePrecise = trialResponseTimeSplit[1]
                    responseTime = responseTimePrecise[0:8]
                    responseDate = trialResponseTimeSplit[0]
                    responseSpeed = (trialResponseTime - trialStartTime).total_seconds()

                    (portResponse, trialResult, turnDirection) = TrialEvaluation(irEast, irWest, nextStim, initPortLocation)

                    #add to trial data file
                    trialNum = OutputTrialData_Response(trialNum, respPortLocation, initPortLocation, portResponse, turnDirection,\
                     trialResult, responseSpeed, initTime, responseTime, responseDate)

                    #Countdown til next trial
                    InterTrialCountdown(interTrialDuration_Response)

                    #Select next stim and port
                    (initPortLocation, nextStim, respPortLocation, trialCorrections) =\
                     StimPortSelection(trialResult, trialCorrections, initPortLocation, nextStim, respPortLocation, trialInitProcedure)

                    break

                ##################################################
                ##### end trial if no response during window #####
                ##################################################
                elif (datetime.datetime.now() >= trialHalfTime) and (datetime.datetime.now() < trialEndTime) :
                    if trialHalfTimeSignal == 0:
                        if speakerLocProcedure < 4:
                            if nextStim == stimEast:
                                subprocess.call(SpeakerEast, shell=True)       #switch to east speaker
                            elif nextStim == stimWest:
                                subprocess.call(SpeakerWest, shell=True)       #switch to west speaker
                        elif speakerLocProcedure == 4:
                            subprocess.call(SpeakerNorth, shell=True)       #switch to north speaker
                        subprocess.call(["aplay", nextStim])
                        trialHalfTimeSignal = 1
                elif datetime.datetime.now() >= trialEndTime:
                    (portResponse, trialResult, responseSpeed, responseTime, trialResult, responseDate, turnDirection) = AssignNoResponse()

                    #add to trial data file
                    trialNum = OutputTrialData_NoResponse(trialNum, respPortLocation, initPortLocation, portResponse, turnDirection,\
                     trialResult, responseSpeed, initTime, responseTime, responseDate)

                    #time.sleep(3)           #gives time for port to turn off before sound plays
                    print "No Response"
                    #subprocess.call(["aplay", trialOverStim])
                    #subprocess.call(["aplay", trialOverStim])

                    #Countdown til next trial
                    InterTrialCountdown(interTrialDuration_NoResponse)

                    #Select next stim and port
                    initPortLocation, nextStim, respPortLocation, trialCorrections =\
                     StimPortSelection(trialResult, trialCorrections, initPortLocation, nextStim, respPortLocation, trialInitProcedure)
                    break

    ###########################################################################
    #######################    South Port Initiate     ########################
    ###########################################################################
    if initPortLocation == 'S':
        SendInitPortSignal(initPortLocation)
        irDetectorState = serSouth.readline()
        #print irDetectorState

        #if beam break detected
        if len(irDetectorState) == 8:       #length of "broken\n" (from arduino code)
            print "Beam Break Detected at South Port"
            if speakerLocProcedure == 1:
                if nextStim == stimEast:
                    subprocess.call(SpeakerEast, shell=True)       #switch to east speaker
                elif nextStim == stimWest:
                    subprocess.call(SpeakerWest, shell=True)       #switch to west speaker
            elif speakerLocProcedure > 1:
                subprocess.call(SpeakerSouth, shell=True)       #switch to north speaker
            subprocess.call(["aplay", nextStim])
            time.sleep(1)
            if speakerLocProcedure == 1 or speakerLocProcedure == 2:
                if nextStim == stimEast:
                    subprocess.call(SpeakerEast, shell=True)       #switch to east speaker
                elif nextStim == stimWest:
                    subprocess.call(SpeakerWest, shell=True)       #switch to west speaker
            elif speakerLocProcedure > 2:
                subprocess.call(SpeakerSouth, shell=True)
            #subprocess.call(["aplay", nextStim])
            trialStartTime = datetime.datetime.now()        #Get time of trial initiation
            trialInitTime = str(datetime.datetime.now()).split(' ')
            trialInitTimePrecise = trialInitTime[1]
            initTime = trialInitTimePrecise[0:8]
            initDate = trialInitTime[0]
            trialHalfTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow/2)
            trialHalfTimeSignal = 0
            trialEndTime = datetime.datetime.now() + datetime.timedelta(seconds=responseWindow)
            print "............................."
            time.sleep(responsePortDelay)

            while True:
                #send signals to arduino to flash East and West LEDs
                if nextStim == stimEast:
                    SendStimEastSignal()
                elif nextStim == stimWest:
                    SendStimWestSignal()

                #check east and west IR-Detectors
                irEast = serEast.readline()
                irWest = serWest.readline()

                #check for beam break at East and West IR-Detectors
                if (len(irEast) == 8) or (len(irWest) == 8):
                    trialResponseTime = datetime.datetime.now()
                    trialResponseTimeSplit = str(datetime.datetime.now()).split(' ')
                    responseTimePrecise = trialResponseTimeSplit[1]
                    responseTime = responseTimePrecise[0:8]
                    responseDate = trialResponseTimeSplit[0]
                    responseSpeed = (trialResponseTime - trialStartTime).total_seconds() #- 7

                    (portResponse, trialResult, turnDirection) = TrialEvaluation(irEast, irWest, nextStim, initPortLocation)

                    #add to trial data file
                    trialNum = OutputTrialData_Response(trialNum, respPortLocation, initPortLocation, portResponse, turnDirection,\
                     trialResult, responseSpeed, initTime, responseTime, responseDate)

                    #Countdown til next trial
                    InterTrialCountdown(interTrialDuration_Response)

                    #Select next stim and port
                    (initPortLocation, nextStim, respPortLocation, trialCorrections) =\
                     StimPortSelection(trialResult, trialCorrections, initPortLocation, nextStim, respPortLocation, trialInitProcedure)
                    break

                ##################################################
                ##### end trial if no response during window #####
                ##################################################
                elif (datetime.datetime.now() >= trialHalfTime) and (datetime.datetime.now() < trialEndTime) :
                    if trialHalfTimeSignal == 0:
                        if speakerLocProcedure < 4:
                            if nextStim == stimEast:
                                subprocess.call(SpeakerEast, shell=True)       #switch to east speaker
                            elif nextStim == stimWest:
                                subprocess.call(SpeakerWest, shell=True)       #switch to west speaker
                        elif speakerLocProcedure == 4:
                            subprocess.call(SpeakerSouth, shell=True)       #switch to north speaker
                        subprocess.call(["aplay", nextStim])
                        trialHalfTimeSignal = 1
                elif datetime.datetime.now() >= trialEndTime:
                    (portResponse, trialResult, responseSpeed, responseTime, trialResult, responseDate, turnDirection) = AssignNoResponse()

                    #add to trial data file
                    trialNum = OutputTrialData_NoResponse(trialNum, respPortLocation, initPortLocation, portResponse, turnDirection,\
                     trialResult, responseSpeed, initTime, responseTime, responseDate)

                    #time.sleep(3)           #gives time for port to turn off before sound plays
                    print "No Response"
                    #subprocess.call(["aplay", trialOverStim])
                    #subprocess.call(["aplay", trialOverStim])

                    #Countdown til next trial
                    InterTrialCountdown(interTrialDuration_NoResponse)

                    #Select next stim and port
                    initPortLocation, nextStim, respPortLocation, trialCorrections =\
                     StimPortSelection(trialResult, trialCorrections, initPortLocation, nextStim, respPortLocation, trialInitProcedure)
                    break

############################################################################
###################   Exit Training Protocol   #############################
############################################################################
time.sleep(5)
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
