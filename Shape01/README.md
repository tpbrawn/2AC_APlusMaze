The **Shape01** folder contains code and related files for operantly training rodents on how to interact with response port modules on a plus maze. 

**Python Files**:   

- Shape01_4PortTrials_V01.py (required)  

**Notes**: This program coordinates with each arduino and outputs data into text file.  Set the maximum number of trials for each response port within the python code (e.g., maxTrialsWest = 10, maxTrialsSouth = 10, etc.)

**Usage**:``` python Shape01_4PortTrials_V01.py --SID 009 --Num 01```  

**Arguments**:
  - -h, --help 			Show this help message and exit
  - --SID #			    Set subject ID: --SID 001
  - --Num #			    Set daily procedure number^: --ProcNum 1
  
^Procedure number is set to differentiate files when more than one session is run per day.

**Arduino Files**
- Shap01_4PortTrials_V02.ino

**Usage**: Upload the same Arduino file to each of the 4 arduinos.  

**Notes** You should re-upload the arduino file to each arduino before starting each session. If the arduino has entered the exit loop in a prior session, the arduino remains in the exit loop for that response port module and will not be active until it is re-uploaded.


