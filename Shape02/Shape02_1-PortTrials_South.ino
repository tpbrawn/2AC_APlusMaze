//Declare pin functions for dual stepper driver
//note: stepper driver not needed for South
#define stp 2
#define dir 3
#define MS1 4
#define MS2 5
#define EN  6

//Declare pins on arduino
#define SENSORPIN 11               //IR sensor
#define LEDPIN 12                  //LED

//Initialize variables
int incomingByte;                  //variable to read incoming serial data into
int sensorState = 0;               //current IR detector state
int interTrialInterval = 5000;     //5 seconds til next trial begins
int exitState = 0;                 //do not enter exit condition
int exitDelay = 5000;              //duration of light flash after python program exits//initialize the stepper library on pins 8 thru 11
int stepCount;                     //index for number of steps the motor turns
int maxSteps = 2000;               //max number of steps the motor turns

void setup() 
{
  // initialize I/Os
  pinMode(LEDPIN, OUTPUT);
  pinMode(SENSORPIN, INPUT);
  digitalWrite(SENSORPIN, HIGH);  
  digitalWrite(LEDPIN, LOW);

  //intialize I/Os for stepper driver
  pinMode(stp, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(EN, OUTPUT);

  Serial.begin(9600);              //initialize serial
}

void loop() 
{
  incomingByte = Serial.read();    //read byte being sent from python

  if (incomingByte == 'X')         //exit condition 'X' sent from python at end of program
  {
    exitLoop();                    //keeps arduino from dispensing food after training completion
  }
    
  else if (incomingByte == 'S')    //'S' sent from python to activate South response port 
  {
    sensorState = digitalRead(SENSORPIN); // check if the sensor beam is broken (i.e., LOW)

    if (sensorState == 0)
    {
      digitalWrite(LEDPIN, LOW);
      Serial.println("Broken");    //"broken" is needed for python...which checks for string length    
      StepperMotorReward();      //dispense reward
      clearReadBuffer();           //1st clear buffer; this is necessary      
      delay(interTrialInterval);
      clearReadBuffer();           //2nd clear buffer; this is necessary
    }
    
    else if (sensorState == 1)
    {
      digitalWrite(LEDPIN, HIGH);  //turn on LED
      delay(100);                  //this delay is necessary:
                                   //     --smaller value leads to flashing
                                   //     --larger value increases interval for checking sensorState
    }
  }
  
  else
  {
      digitalWrite(LEDPIN, LOW);  //if incomingByte is not 'X' or 'S'...turn off LED
  }  
}

void StepperMotorReward()
//motor is stepping at 1/8th microstep mode
{
  digitalWrite(dir, HIGH); //Pull direction pin high to move "forward"
  digitalWrite(MS1, HIGH); //Pull MS1 and MS2 high to set logic to 1/8th microstep resolution
  digitalWrite(MS2, HIGH);
  delay(1000);             //delay period before motor begins stepping
  
  for (stepCount = 1; stepCount < maxSteps; stepCount++) //Loop for forward stepping
  {
    digitalWrite(stp, HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp, LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}

void clearReadBuffer()
{
  while(Serial.available() > 0) 
      {
        char t = Serial.read();
      }
}

void exitLoop()
{
   while (incomingByte == 'X' || exitState == 1)
    {
      digitalWrite(LEDPIN, LOW);
      delay(exitDelay);
      digitalWrite(LEDPIN, HIGH);
      delay(500);
      digitalWrite(LEDPIN, LOW);
      exitState=1;
    }
}

