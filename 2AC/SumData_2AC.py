################################################################################
############################   SumData_2AC.py  #################################
################################################################################
#This program reads the TrialData.txt file output from 2AC and provides
#a summary of the results:
# - number of trials completed
# - number of correct trial: total and per stimulus type
# - number of east and west responses (response bias)
# - number of left and right Turns
# - average response times

################################################################################

############################################################################
#########################   import libraries   #############################
############################################################################
import argparse
import itertools
############################################################################
######################   parse command line  ###############################
############################################################################
parser = argparse.ArgumentParser()
parser.add_argument("--F", help="set file name: e.g. --F 007_2AC_TrialData_080918-01.txt")
args = parser.parse_args()
if args.F:
    trialDataFile = args.F
else:
    print("Trial Data File required: e.g., --F 007_2AC_TrialData_080918-01.txt")
    raise SystemExit
############################################################################
#####################   initialize data file   #############################
############################################################################
findST = "Time:"
filename =  trialDataFile[0:3] + "_2AC_SumData_" + trialDataFile[18:31]
sumData = open(filename, "w")
sumData.write("********************************************\n")
sumData.write("********************************************\n")
sumData.write("*  Filename: %s\n" %filename)
sumData.write("********************************************\n")
sumData.write("********************************************\n")
sumData.write("*        TrialData Header Info:\n")
sumData.write("********************************************\n")
trialData = open(trialDataFile, "r")
for line in range(1,12):
    line = trialData.readline()
    if line.find(findST) > 0:
        print line
    sumData.write("*  ")
    sumData.write(line)
sumData.write("********************************************\n")
sumData.write("********************************************\n")
sumData.write("\n\n")
sumData.write("********************************************\n")
sumData.write("          Trial Data Summary:\n")
sumData.write("********************************************\n")
trialData.close()

############################################################################
#######################   analyze data file   ##############################
############################################################################

########################
#count number of trials
########################
trialData = open(trialDataFile, "r")            #open trialData to read from beginning
filelength = len(trialData.readlines())         #get number of lines in file
#print "Number of lines in file: %d\n" %filelength
numTrials = filelength-16                       #subtract 16 due to number of header lines
print "Number of trials initiated: %d" %numTrials
sumData.write("Number of trials initiated: %d\n" %numTrials)
trialData.close()

##################################
#count number of completed trials
##################################
findX = "X"                                                 #search for "X" in line, which indicates incomplete trial
completeTrials = 0
incompleteTrials = 0                                         #initialize completedTrials
trialData = open(trialDataFile, "r")                        #open trialData to read from beginning
for line in itertools.islice(trialData,16,filelength):      #loop thru first data line to end of file
    if line.find(findX) < 0:
        completeTrials += 1
    elif line.find(findX) > 0:
        incompleteTrials += 1
print "Number of finished trials: %d" %completeTrials
print "Number of unfinished trials: %d" %incompleteTrials
sumData.write("Number of finished trials: %d\n" %completeTrials)
sumData.write("Number of unfinished trials: %d\n" %incompleteTrials)

###############################
#compute completion percentage
###############################
completionPercentage = (float(completeTrials)/numTrials)*100
print "Percentage of trials completed: %.2f%%\n" %completionPercentage
sumData.write("Percentage of trials completed: %.2f%%\n" %completionPercentage)
sumData.write("\n")
trialData.close()

################################
#count number of correct trials
################################
trialData = open(trialDataFile, "r")              #open trialData to read from beginning

#initialize find statements
find1 = "1"
findE = "E"
findW = "W"
findN = "N"
findS = "S"

#initialize correct and incorrect trial counts
correct = 0
incorrect = 0
correctStimE = 0
incorrectStimE = 0
correctStimW = 0
incorrectStimW = 0
correctRespE = 0
incorrectRespE = 0
correctRespW = 0
incorrectRespW = 0
correctN = 0
incorrectN = 0
correctS = 0
incorrectS = 0
TurnR = 0
TurnL = 0
TrialsTurnL = 0
TrialsTurnR = 0

for line in itertools.islice(trialData,16,filelength):

    #count total number of correct trials
    if line.find(findX) > 0:   #skip incomplete trials
        continue

    if line.find(find1,56,61) > 0:
        correct += 1
    elif line.find(find1,56,61) < 0:
        incorrect +=1

    #count number of correct trials with Stim-E:
    if line.find(findE,13,15) > 0 and line.find(find1,56,61) > 0:
        correctStimE += 1
    elif line.find(findE,13,15) > 0 and line.find(find1,56,61) < 0:
        incorrectStimE += 1

    #count number of correct trials with Stim-W:
    if line.find(findW,13,15) > 0 and line.find(find1,56,61) > 0:
        correctStimW += 1
    elif line.find(findW,13,15) > 0 and line.find(find1,56,61) < 0:
        incorrectStimW += 1

    #count number of correct trials initiated at North Port
    if line.find(findN,18,25) > 0 and line.find(find1,56,61) > 0:
        correctN += 1
    elif line.find(findN,18,25) > 0 and line.find(find1,56,61) < 0:
        incorrectN += 1

    #count number of correct trials initiated at South Port
    if line.find(findS,18,25) > 0 and line.find(find1,56,61) > 0:
        correctS += 1
    elif line.find(findS,18,25) > 0 and line.find(find1,56,61) < 0:
        incorrectS += 1

    #count number of Left or Right Turns
    if line.find(findN,18,25) > 0 and line.find(findE,38,44) > 0:
        TurnL += 1
    elif line.find(findN,18,25) > 0 and line.find(findW,38,44) > 0:
        TurnR += 1
    elif line.find(findS,18,25) > 0 and line.find(findE,38,44) > 0:
        TurnR += 1
    elif line.find(findS,18,25) > 0 and line.find(findW,38,44) > 0:
        TurnL += 1

    #count number of trials requiring left or right turns
    if line.find(findN,18,25) > 0 and line.find(findE,28,35) > 0:
        TrialsTurnL += 1
    elif line.find(findN,18,25) > 0 and line.find(findW,28,35) > 0:
        TrialsTurnR += 1
    elif line.find(findS,18,25) > 0 and line.find(findE,28,35) > 0:
        TrialsTurnR += 1
    elif line.find(findS,18,25) > 0 and line.find(findW,28,35) > 0:
        TrialsTurnL += 1

#####################
#compute percentages
#####################
percentCorrect = (float(correct)/(correct+incorrect))*100
percentCorrect_StimE = (float(correctStimE)/(correctStimE+incorrectStimE))*100
percentCorrect_StimW = (float(correctStimW)/(correctStimW+incorrectStimW))*100
percentCorrectNorth = (float(correctN)/(correctN+incorrectN))*100
percentCorrectSouth = (float(correctS)/(correctS+incorrectS))*100

print "Number of Correct Trials: %d" %correct
print "Number of Incorrect Trials: %d" %incorrect
print "Correct Trial Percent: %.2f%%\n" %percentCorrect
sumData.write("Number of Correct Trials: %d\n" %correct)
sumData.write("Number of Incorrect Trials: %d\n" %incorrect)
sumData.write("Correct Trial Percent: %.2f%%\n\n" %percentCorrect)

print "Number of Correct Stim-E Trials: %d" %correctStimE
print "Number of Incorrect Stim-E-Trials: %d" %incorrectStimE
print "Correct Stim-E Trial Percent: %.2f%%\n" %percentCorrect_StimE
sumData.write("Number of Correct Stim-E Trials: %d\n" %correctStimE)
sumData.write("Number of Incorrect Stim-E Trials: %d\n" %incorrectStimE)
sumData.write("Correct Stim-E Trial Percent: %.2f%%\n\n" %percentCorrect_StimE)

print "Number of Correct Stim-W Trials: %d" %correctStimW
print "Number of Incorrect Stim-W-Trials: %d" %incorrectStimW
print "Correct Stim-W Trial Percent: %.2f%%\n" %percentCorrect_StimW
sumData.write("Number of Correct Stim-W Trials: %d\n" %correctStimW)
sumData.write("Number of Incorrect Stim-W Trials: %d\n" %incorrectStimW)
sumData.write("Correct Stim-W Trial Percent: %.2f%%\n\n" %percentCorrect_StimW)

print "Number of Correct North-Initiated Trials: %d" %correctN
print "Number of Incorrect North-Initiated Trials: %d" %incorrectN
print "Correct North-Initiated Trial Percent: %.2f%%\n" %percentCorrectNorth
sumData.write("Number of Correct North-Initiated Trials: %d\n" %correctN)
sumData.write("Number of Incorrect North-Initiated Trials: %d\n" %incorrectN)
sumData.write("Correct North-Initiated Trial Percent: %.2f%%\n\n" %percentCorrectNorth)

print "Number of Correct South-Initiated Trials: %d" %correctS
print "Number of Incorrect South-Initiated Trials: %d" %incorrectS
print "Correct South-Initiated Trial Percent: %.2f%%\n" %percentCorrectSouth
sumData.write("Number of Correct South-Initiated Trials: %d\n" %correctS)
sumData.write("Number of Incorrect South-Initiated Trials: %d\n" %incorrectS)
sumData.write("Correct South-Initiated Trial Percent: %.2f%%\n\n" %percentCorrectSouth)

#################################################
#compute East-West response bias
#################################################
trialData = open(trialDataFile, "r")              #open trialData to read from beginning

findE = "E"
findW = "W"
eastResponse = 0
westResponse = 0

for line in itertools.islice(trialData,16,filelength):
    if line.find(findE,38,43) > 0:
        eastResponse += 1
    elif line.find(findW,38,43) > 0:
        westResponse += 1
eastResponseRate = float(eastResponse)/(eastResponse+westResponse)*100
westResponseRate = float(westResponse)/(eastResponse+westResponse)*100
print "number of East port responses: %d (%.2f%%)" %(eastResponse, eastResponseRate)
print "number of West port responses: %d (%.2f%%)\n" %(westResponse, westResponseRate)
sumData.write("number of East port responses: %d (%.2f%%)\n" %(eastResponse, eastResponseRate))
sumData.write("number of West port responses: %d (%.2f%%)\n\n" %(westResponse, westResponseRate))
trialData.close()

#################################################
#Left-Right Turn bias
#################################################
trialData = open(trialDataFile, "r")              #open trialData to read from beginning
TurnR_Rate = float(TurnR)/(TurnR + TurnL)*100
TurnL_Rate = float(TurnL)/(TurnR + TurnL)*100
TrialsTurnR_Rate = float(TrialsTurnR)/(TrialsTurnR + TrialsTurnL)*100
TrialsTurnL_Rate = float(TrialsTurnL)/(TrialsTurnR + TrialsTurnL)*100
print "Number of Right Turns: %d (%.2f%%)" %(TurnR, TurnR_Rate)
print "Number of Left Turns: %d (%.2f%%)\n" %(TurnL, TurnL_Rate)
print "Number of Right-Turn Trials: %d (%.2f%%)" %(TrialsTurnR, TrialsTurnR_Rate)
print "Number of Left-Turn Trials: %d (%.2f%%)\n" %(TrialsTurnL, TrialsTurnL_Rate)
sumData.write("number of Right Turns: %d (%.2f%%)\n" %(TurnR, TurnR_Rate))
sumData.write("number of Left Turns: %d (%.2f%%)\n\n" %(TurnL, TurnL_Rate))
sumData.write("number of Right-Turn Trials: %d (%.2f%%)\n" %(TrialsTurnR, TrialsTurnR_Rate))
sumData.write("number of Left-Turn Trials: %d (%.2f%%)\n\n" %(TrialsTurnL, TrialsTurnL_Rate))
trialData.close()

#####################################################
#compute response time average: all completed trials
#####################################################
trialData = open(trialDataFile, "r")              #open trialData to read from beginning
count=0
RTsum = 0.0
for line in itertools.islice(trialData,16,filelength):
    if count < 9 and line.find(findX) < 0:
        RTfloat = float(line[64:72])
        count += 1
        RTsum += RTfloat
    elif count >= 9 and line.find(findX) < 0:
        RTfloat = float(line[64:72])
        count += 1
        RTsum += RTfloat
responseTimeAVG = RTsum/count
print "Average response time for all trials: %.2f seconds" %responseTimeAVG
sumData.write("Average response time for all trials: %.2f seconds\n" %responseTimeAVG)
trialData.close

################################################
#compute response time average: correct trials
################################################
trialData = open(trialDataFile, "r")              #open trialData to read from beginning
count=0
RTsum = 0.0
for line in itertools.islice(trialData,16,filelength):
    if count < 9 and line.find(findX) < 0 and line.find(find1,56,61) > 0:
        RTfloat = float(line[64:72])
        count += 1
        RTsum += RTfloat
    elif count >= 9 and line.find(findX) < 0 and line.find(find1,56,61) > 0:
        RTfloat = float(line[64:72])
        count += 1
        RTsum += RTfloat
responseTimeAVG_Correct = RTsum/count
print "Average response time for correct trials: %.2f seconds" %responseTimeAVG_Correct
sumData.write("Average response time for correct trials: %.2f seconds\n" %responseTimeAVG_Correct)
trialData.close

#################################################
#compute response time average: incorrect trials
#################################################
trialData = open(trialDataFile, "r")              #open trialData to read from beginning
count=0
RTsum = 0.0
for line in itertools.islice(trialData,16,filelength):
    if count < 9 and line.find(findX) < 0 and line.find(find1,56,61) < 0:
        RTfloat = float(line[64:72])
        count += 1
        RTsum += RTfloat
    elif count >= 9 and line.find(findX) < 0 and line.find(find1,56,61) < 0:
        RTfloat = float(line[64:72])
        count += 1
        RTsum += RTfloat
responseTimeAVG_Incorrect = RTsum/count
print "Average response time for incorrect trials: %.2f seconds\n" %responseTimeAVG_Incorrect
sumData.write("Average response time for incorrect trials: %.2f seconds\n\n" %responseTimeAVG_Incorrect)
trialData.close
sumData.close()
