from dronekit import connect, VehicleMode
import time
import tkinter as tk
import speech_recognition as sr
from custom_object_detection import ObjectDetection

connection_string = 'COM9' # Replace with the serial port of your Pixhawk
baud_rate = 57600 # Replace with the baud rate that your Pixhawk is configured to use
vehicle = connect(connection_string, baud=baud_rate, wait_ready=False)

# Set the mode of the vehicle to MANUAL
vehicle.mode = VehicleMode("MANUAL")

# Arm the vehicle
vehicle.armed = True

detection = ObjectDetection("C:/Users/chotu/Desktop/ps/best (6).pt")


print("q")

def forward():
   vehicle.channels.overrides['3'] = 1300

def backward():
  vehicle.channels.overrides['3'] = 1800
  time.sleep(1)
  vehicle.channels.overrides['3'] = 1500
  vehicle.channels.overrides['1'] = 1500


# Turn right
def right():
  vehicle.channels.overrides['3'] = 1500
  vehicle.channels.overrides['1'] = 1800

#left
def left():
  vehicle.channels.overrides['3'] = 1500
  vehicle.channels.overrides['1'] = 1100
  

def move():
  while True:
    areas , center = detection()
    if center[0] < 315 :
      left()
      vehicle.channels.overrides['3'] = 1500
      vehicle.channels.overrides['1'] = 1500
    elif center[0] > 325 :
      right()
      vehicle.channels.overrides['3'] = 1500
      vehicle.channels.overrides['1'] = 1500
    else:
      forward()
      if areas >= 274000 and areas <= 280000 :
        vehicle.channels.overrides['3'] = 1500
        vehicle.channels.overrides['1'] = 1500
        break

def key(event):
    if event.char == event.keysym:  # Standard keys
        if event.keysym == 'q':
            print("QUIT")
            vehicle.armed = False
            vehicle.close()
            exit()
        elif event.keysym == 'r':
            # Add RTL mode implementation
            pass
    else:  # Non-standard keys
        if event.keysym == 'Up':
            forward()
        elif event.keysym == 'Down':
            move()
        elif event.keysym == 'Right': 
            right()
        elif event.keysym == 'Left':
            left()
        elif event.keysym == 'space': 
            print('hi')
            recognize_live_voice_command()


def recognize_live_voice_command():
    # Create a recognizer object
    r = sr.Recognizer()
    
    # with sr.Microphone(device_index=1) as source:
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening...")

        # Continuously listen for voice commands in real-time
        while True:
            try:
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source)

                # Listen for the user's voice command
                audio = r.listen(source)
                # Recognize speech using Google Speech Recognition
                command = r.recognize_google(audio)
                print("Voice command:", command)

                # Process the recognized command
                process_voice_command(command)
            except sr.UnknownValueError:
                print("Speech recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

def process_voice_command(command):
    if 'forward' in command:
        forward()
    elif 'backward' in command:
        backward()
    elif 'right' in command:
        right()
    elif 'left' in command:
        left()
    # Add more voice commands and corresponding actions as needed
    elif 'move' in command:
        move()
    else:
        print("Unrecognized voice command")


print("q")

root = tk.Tk()
print(">> Control the drone with the arrow keys. Press r for RTL mode")
root.bind_all('<Key>', key)
root.mainloop()