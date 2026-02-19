void setup() {
  // 1. Initialize communication with your computer (Serial Monitor)
  Serial.begin(9600);
  
  // 2. Initialize communication with the Minitel on Serial1 (Pins 18 & 19)
  // Minitel requires: 1200 baud, 7 data bits, Even parity, 1 stop bit
  Serial1.begin(1200, SERIAL_7E1);
  
  // 3. Enable the internal pull-up resistor on the Mega's RX1 pin (Pin 19)
  // This is crucial because the Minitel's TX line is open-collector
  pinMode(19, INPUT_PULLUP);

  // Give the serial ports a brief moment to stabilize
  delay(100);

  // Send a startup message to your computer's Serial Monitor
  Serial.println("Arduino to Minitel Bridge Initialized.");
  Serial.println("Type here to send text to the Minitel...");

  // Send a startup message to the Minitel screen
  Serial1.println("Hello Minitel!");
  Serial1.println("Connection established.");
}

void loop() {
  // 4. Read from the Computer and send to the Minitel
  if (Serial.available() > 0) {
    char pcData = Serial.read();
    Serial1.write(pcData);
  }

  // 5. Read from the Minitel and send to the Computer
  if (Serial1.available() > 0) {
    char minitelData = Serial1.read();
    Serial.write(minitelData);
    
    // THE MINITEL QUIRK: Local Echo
    // Minitels do not automatically display what you type on their own screen. 
    // They expect the host computer to "echo" the character back to them.
    // Uncomment the line below if you want to see your typing on the Minitel screen:
    
    // Serial1.write(minitelData); 
  }
}