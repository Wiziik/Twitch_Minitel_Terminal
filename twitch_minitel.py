import socket
import serial
import re
import time
import textwrap

# --- 1. CONFIGURATION ---
SERIAL_PORT = '/dev/ttyUSB0'           # Raspberry Pi USB port
BAUD_RATE = 9600                       # Must match Serial.begin() in Arduino
TWITCH_SERVER = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667

# Replace these with your actual details:
TWITCH_NICKNAME = 'tv_store'     # Your username (lowercase)
TWITCH_TOKEN = 'oauth:vwkwmosbivjam57lj4yvex59mwh21h' # Keep the "oauth:" and paste your new token after it
TWITCH_CHANNEL = '#TV_STORE'        # The channel to read (must start with #)

# --- 2. CONNECT TO ARDUINO ---
try:
    print(f"Connecting to Arduino on {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Give Arduino time to reset upon connection
    print("Arduino connected!")
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    print("Tip: If you get Permission Denied, run: sudo usermod -aG dialout $USER")
    exit()

# --- 3. CONNECT TO TWITCH ---
sock = socket.socket()
sock.connect((TWITCH_SERVER, TWITCH_PORT))
sock.send(f"PASS {TWITCH_TOKEN}\n".encode('utf-8'))
sock.send(f"NICK {TWITCH_NICKNAME}\n".encode('utf-8'))
sock.send(f"JOIN {TWITCH_CHANNEL}\n".encode('utf-8'))
print(f"Connected to Twitch channel: {TWITCH_CHANNEL}")

# --- 4. LISTEN AND SEND LOOP ---
while True:
    try:
        resp = sock.recv(2048).decode('utf-8', errors='ignore')
        
        # Twitch requires us to play ping-pong to stay connected
        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))
            
        elif len(resp) > 0:
            # Look for standard chat messages using regex
            match = re.search(r':(\w+)\!.*PRIVMSG\s+#\w+\s+:(.*)', resp)
            if match:
                username = match.group(1)
                message = match.group(2).strip()
                
                # CRUCIAL MINITEL STEP: Strip Emojis and special characters!
                # Minitel only understands basic ASCII. UTF-8 emojis will print garbage.
                clean_msg = message.encode('ascii', 'ignore').decode('ascii')
                
                # Format the full string
                full_message = f"{username}: {clean_msg}"
                
                # Wrap text to fit the Minitel's 40-character column limit
                wrapped_lines = textwrap.wrap(full_message, width=40)
                
                for line in wrapped_lines:
                    print(line) # Print to Raspberry Pi terminal
                    
                    # Send to Arduino/Minitel with Carriage Return (\r) + Line Feed (\n)
                    ser.write(f"{line}\r\n".encode('ascii'))
                    
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        sock.close()
        ser.close()
        break
    except Exception as e:
        print(f"Error: {e}")