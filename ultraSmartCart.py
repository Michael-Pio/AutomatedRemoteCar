import socket
import json
import time
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import asyncio
from ultralytics import YOLO

# Define server address and port
UDP_IP = "192.168.139.135"  # Replace with the IP address of your ESP8266
UDP_PORT = 4210

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Load the YOLO model trained to detect humans
model = YOLO("yolo11n.pt")

# Initialize video capture
camUri = 0  # For local webcam; use your IP camera URI if needed
# camUri = r"http://192.168.139.117:6677/videofeed?username=&password="
cap = cv2.VideoCapture(camUri)

# Command state and video capture frame
last_command = None
last_sent_time = 0
command_interval = 0.05  # Minimum time interval between sending commands (50 ms)
manual_mode = True  # Toggle state for manual/auto mode
process_frame_interval = 3  # Process every 3rd frame
frame_count = 0

# UI button states
button_colors = {"normal": "#ccc", "active": "#f55"}
button_map = {}

# Function to send command via UDP
def send_command(direction, speed=75):
    global last_command, last_sent_time
    current_time = time.time()

    # Send only if command is different or enough time has elapsed
    if direction != last_command or (current_time - last_sent_time) >= command_interval:
        command = json.dumps({"direction": direction, "speed": speed})
        sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent: {command}")
        last_command = direction
        last_sent_time = current_time

# Toggle between manual and auto modes
def toggle_mode():
    global manual_mode
    manual_mode = not manual_mode
    mode_label.config(text=f"Mode: {'Manual' if manual_mode else 'Auto'}")
    print(f"Switched to {'Manual' if manual_mode else 'Auto'} mode")

# Key press handler for manual control
def on_key_press(event):
    if manual_mode:
        key = event.keysym.lower()
        if key == 'w':
            send_command("FWD", 75)
            highlight_button("w")
        elif key == 's':
            send_command("BWD", 75)
            highlight_button("s")
        elif key == 'a':
            send_command("LFT", 75)
            highlight_button("a")
        elif key == 'd':
            send_command("RGT", 75)
            highlight_button("d")
        elif key == 'q':
            send_command("STP", 0)
            highlight_button("q")
        elif key == 'e':
            print("Exiting...")
            root.quit()

def on_key_release(event):
    if manual_mode:
        key = event.keysym.lower()
        if key in button_map:
            reset_button_color(key)

def highlight_button(key):
    if key in button_map:
        button_map[key].config(bg=button_colors["active"])

def reset_button_color(key):
    if key in button_map:
        button_map[key].config(bg=button_colors["normal"])

# YOLO-based auto control logic
async def auto_control():
    global last_command, frame_count
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    center_x = frame_width // 2
    tolerance = 50

    while not manual_mode:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Only process every nth frame to reduce load
        frame_count += 1
        if frame_count % process_frame_interval != 0:
            await asyncio.sleep(0)
            continue

        # Run YOLO model on the current frame
        results = model(frame)
        human_detected = None
        for detection in results[0].boxes:
            if detection.cls == 0:  # Assuming 0 is the human class ID
                human_detected = detection
                break

        # Determine movement commands based on human position
        command = None
        if human_detected:
            x_min, y_min, x_max, y_max = human_detected.xyxy[0]
            human_center_x = (x_min + x_max) // 2
            if human_center_x < center_x - tolerance:
                command = "LFT"
            elif human_center_x > center_x + tolerance:
                command = "RGT"
            else:
                command = "FWD"
        else:
            command = "STP"

        if command != last_command:
            send_command(command)
            last_command = command

        # Display the frame with the command
        cv2.putText(frame, command, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Robot Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# Frame update loop for video feed
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    if not manual_mode:
        asyncio.run(auto_control())
    root.after(10, update_frame)

# Initialize the GUI
root = tk.Tk()
root.title("RC Car Controller")

# Toggle mode button
mode_label = tk.Label(root, text="Mode: Manual")
mode_label.pack(pady=5)
toggle_button = tk.Button(root, text="Toggle Mode", command=toggle_mode)
toggle_button.pack(pady=5)

# Bind keys for control
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

# Create a frame for the video
video_frame = ttk.Frame(root)
video_frame.pack(padx=10, pady=10)
video_label = tk.Label(video_frame)
video_label.pack()

# Create a frame for control keys
controls_frame = ttk.Frame(root)
controls_frame.pack(pady=10)

# Create buttons for W, A, S, D, Q, E
button_map['w'] = tk.Button(controls_frame, text='W', width=5, height=2, bg=button_colors["normal"])
button_map['a'] = tk.Button(controls_frame, text='A', width=5, height=2, bg=button_colors["normal"])
button_map['s'] = tk.Button(controls_frame, text='S', width=5, height=2, bg=button_colors["normal"])
button_map['d'] = tk.Button(controls_frame, text='D', width=5, height=2, bg=button_colors["normal"])
button_map['q'] = tk.Button(controls_frame, text='Q = Stop', width=10, height=2, bg=button_colors["normal"])
button_map['e'] = tk.Button(controls_frame, text='E = Exit', width=10, height=2, bg=button_colors["normal"])

# Grid layout for control buttons
button_map['w'].grid(row=0, column=1, padx=5, pady=5)
button_map['a'].grid(row=1, column=0, padx=5, pady=5)
button_map['s'].grid(row=1, column=1, padx=5, pady=5)
button_map['d'].grid(row=1, column=2, padx=5, pady=5)
button_map['q'].grid(row=2, column=0, columnspan=2, padx=5, pady=5)
button_map['e'].grid(row=2, column=1, columnspan=2, padx=5, pady=5)

# Start video update loop
update_frame()
root.mainloop()

# Cleanup
cap.release()
sock.close()
