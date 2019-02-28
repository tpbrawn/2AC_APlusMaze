The **Shape02** folder contains code and related files for operantly shaping rodents in preparation for a two-alternative choice auditory classification task on an automated plus maze. 

This program shines one of the four LEDs (north, east, south, west) and waits for response via beam break of associated IR detector. Upon response, reward is given from syringe pump and one of the other ports randomly shines again and awaits response via the associated IR detector.

**Python Files**:   

- Shape02_1-PortTrials_V01.py (required)  

**Notes**: This program coordinates with each arduino, selects the active port, and outputs response data into text file.  

**Usage**:``` python Shape02_1-PortTrials_V01.py --SID 014 --Num 01```  

**Arguments**:
  - -h, --help 			Show this help message and exit
  - --SID #			    set subject ID: --SID 001
  - --Num #			    set daily procedure number^: --ProcNum 1

^Procedure number is set to differentiate files when more than one session is run per day.  

**Arduino Files**
- Shape02_1-PortTrials_North.ino
- Shape02_1-PortTrials_East.ino
- Shape02_1-PortTrials_South.ino
- Shape02_1-PortTrials_West.ino

**Usage**: Upload each Arduino file to its respective Arduino (e.g., Shape02_East.ino to the East arm response port module).  For each file, set the maxSteps variable (e.g., maxSteps = 2000) to adjust the amount of reward delivery and the beamBreakThreshold variable (e.g., beamBreakThreshold = 5) to set the duration that the animal has to maintain beamBreak to trigger a response (duration = beamBreakThreshold * 100ms).


