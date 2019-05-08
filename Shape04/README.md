The **Shape04** folder contains code and related files for operantly shaping rodents in preparation for a two-alternative choice auditory classification task on an automated plus maze. 

This program shines one of the two LEDs (north or south) and waits for response via beam break of associated IR detector. Upon response, reward is given from syringe pump (if a reward value is set in the arduino file). The LED from one of the other two ports (east or west) shines and waits for response via beam break of associated IR detector. If a response occurs within the response window duration (set in the python file), then reward is dispensed and a new trial starts after the duration of the responseInterTrialInterval variable (e.g., 5 seconds; set in python file). If no response is detected within the response window, the port inactivates and a new trial is started after duration of the noResponse_InterTrialInterval variable (e.g., 60 seconds).

Shape04 is identical to Shape03 except the arduino files are set to give no reward for north and south port responses. Shape04 is the final step of transitioning rats into completing trials that are initiated at the north or south ports and completed at the east or west ports. At this point, the rat has learned to complete a 2-response trial.   

**Python Files**:   

- Shape04_2PortTrials.py (required)  

**Notes**: This program coordinates with each arduino, selects the active port, and outputs response data into text file.  

**Usage**:``` python Shape04_2PortTrials.py --SID 013 --Num 02```  
Within the python file:
- Set the responseWindow variable (e.g., responseWindow = 30) to adjust how long the animal has to complete an initiated trial. 

**Arguments**:
  - -h, --help 			Show this help message and exit
  - --SID #			    set subject ID: --SID 001
  - --Num #			    set daily procedure number^: --Num 1

^Procedure number is set to differentiate files when more than one session is run per day.  

**Arduino Files**
- Shape04_2PortTrials_North.ino
- Shape04_2PortTrials_East.ino
- Shape04_2PortTrials_South.ino
- Shape04_2PortTrials_West.ino

**Usage**: Upload each Arduino file to its respective Arduino (e.g., Shape04_2PortTrials_East.ino to the East arm response port module).  For each file, set the maxSteps variable (e.g., maxSteps = 2000) to adjust the amount of reward delivery and the beamBreakThreshold variable (e.g., beamBreakThreshold = 5) to set the duration that the animal has to maintain beamBreak to trigger a response (duration = beamBreakThreshold * 100ms).
