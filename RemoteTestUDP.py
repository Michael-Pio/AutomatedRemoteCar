import socket
import json
import keyboard
import time

# Define server address and port
UDP_IP = "192.168.187.135"  # Replace with the IP address of your ESP8266
UDP_PORT = 4210

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Command state to prevent duplicate commands
last_command = None
last_sent_time = 0
command_interval = 0.05  # Minimum time interval between sending commands (50 ms)

def send_command(direction, speed=75):
    global last_command, last_sent_time
    current_time = time.time()

    # Only send if the command is different or if enough time has elapsed
    if direction != last_command or (current_time - last_sent_time) >= command_interval:
        command = json.dumps({"direction": direction, "speed": speed})
        sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent: {command}")
        last_command = direction
        last_sent_time = current_time

def main():
    print("Use W/A/S/D to control the car, Q to stop, and E to exit.")
    
    try:
        while True:
            # Check for keyboard input and send corresponding commands
            if keyboard.is_pressed('w'):
                send_command("FWD", 75)
            elif keyboard.is_pressed('s'):
                send_command("BWD", 75)
            elif keyboard.is_pressed('a'):
                send_command("LFT", 75)
            elif keyboard.is_pressed('d'):
                send_command("RGT", 75)
            elif keyboard.is_pressed('q'):
                send_command("STP", 0)
            elif keyboard.is_pressed('e'):
                print("Exiting...")
                break

            time.sleep(0.01)  # Short delay for responsiveness
    finally:
        sock.close()

if __name__ == "__main__":
    main()
