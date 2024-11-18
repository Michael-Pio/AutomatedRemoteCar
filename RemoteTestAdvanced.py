import socket
import json
import time
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

# Define server address and port
UDP_IP = "192.168.165.135"  # Replace with the IP address of your ESP8266
UDP_PORT = 4210

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Command state to prevent duplicate commands
last_command = None
last_sent_time = 0
command_interval = 0.05  # Minimum time interval between sending commands (50 ms)

# Initialize video capture (0 for the first camera)
cap = cv2.VideoCapture(0)

# UI button states
button_colors = {
    "normal": "#ccc",
    "active": "#f55"
}

# Store button references for easier access
button_map = {}

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

def on_key_press(event):
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
    key = event.keysym.lower()
    if key in button_map:
        reset_button_color(key)

def highlight_button(key):
    if key in button_map:
        button_map[key].config(bg=button_colors["active"])

def reset_button_color(key):
    if key in button_map:
        button_map[key].config(bg=button_colors["normal"])

def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    
    root.after(10, update_frame)

# Initialize the GUI
root = tk.Tk()
root.title("RC Car Controller")

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

# Start the Tkinter main loop
root.mainloop()

# Cleanup
cap.release()
sock.close()
