The **2AC** folder contains code and related files for operantly training rodents on a two-alternative choice auditory classification task on an automated plus maze. 

**Python Files**:   
Main program coordinating with each Arduino, selecting stimulus and initiation ports for each trial, and outputting data in text file.
- 2AC_V02.py (required)      
**Usage**: ```
python 2AC_V02.py --SID 009 --MaxCor 2 --SE B6_triple_1s.wav –SW --C5_single_1s.wav --ProcNum 01
```
- SumData_2AC.py (optional)  
**Usage**: python SumData_2AC.py --F 009_2AC_TrialData_012919-01.txt

**Arguments**:
- -h, --help 			Show this help message and exit
- --SID #			set subject ID: --SID 001
- --MaxCor #			set maximum number of consecutive correction trials^: MaxCor 1
- --SE stimfile			set stimulus for East response port: --SE upsweep.wav
- --SE stimfile			set stimulus for West response port: --SW upsweep.wav
- --ProcNum #			set daily procedure number^^: --ProcNum 1

^Correction trials are initiated after error responses. Correction trials result in the same stimulus and same trial initiation port being selected for the next trial. If MaxCor is set to 0, every the stimulus and trial initiation port will be selected randomly.  If MaxCor is set to 2, the same stimulus and trial initiation port will be selected for up to 2 consecutive error responses, after which the stimulus and trial initiation port will be selected randomly again.  

^^Procedure number is set to differentiate files when more than one session is run per day.

**Arduino Files**
- 2AC_North.ino
- 2AC_East.ino
- 2AC_South.ino
- 2AC_West.ino

**Usage**: Upload each Arduino file to its respective Arduino (e.g., 2AC_East.ino to the East arm response port module).  For the East and West files, set the maxSteps variable (e.g., maxSteps = 2000) to adjust the amount of reward delivery.

### Contributors
-[Tim Brawn](http://www.mit.edu/people/tpbrawn/index.html)
