import asyncio
import json
import socket
from ultralytics import YOLO
import cv2

# Load the YOLO model trained to detect humans
model = YOLO("yolo11n.pt") 
# ESP8266 IP address and UDP port
UDP_IP = "192.168.165.135"  # Replace with your ESP8266's IP address
UDP_PORT = 4210  # Replace with your desired UDP port

# Camera feed URI
camUri = r"http://192.168.165.207:6677/videofeed?username=&password="
camUri = 0

# Function to send command via UDP
def send_udp_command(sock, direction, speed=75):
    command = json.dumps({"direction": direction, "speed": speed})
    sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
    print(f"Sent: {command}")

async def control_robot():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    cap = cv2.VideoCapture(camUri)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    center_x = frame_width // 2
    tolerance = 50  
    last_command = None  # Track the last command to avoid sending duplicates
    process_frame_interval = 3  # Process every 3rd frame
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # Only process every nth frame to reduce load
            frame_count += 1
            if frame_count % process_frame_interval != 0:
                await asyncio.sleep(0)  # Yield control to event loop
                continue  # Skip processing for this frame

            # Run YOLO model on the current frame
            results = model(frame)

            # Find human detection in YOLO results
            human_detected = None
            for detection in results[0].boxes:
                if detection.cls == 0:  # Assuming 0 is the human class ID
                    human_detected = detection
                    break

            # Determine movement commands based on human position
            command = None
            if human_detected:
                x_min, y_min, x_max, y_max = human_detected.xyxy[0]
                human_center_x = (x_min + x_max) // 2  # Horizontal center of detected human

                # Determine direction based on the human position relative to the frame center
                if human_center_x < center_x - tolerance:
                    command = "LFT"  # Turn Left
                elif human_center_x > center_x + tolerance:
                    command = "RGT"  # Turn Right
                else:
                    command = "FWD"  # Go Straight

            else:
                command = "STP"

            # Send command only if it is different from the last command sent
            if command != last_command:
                send_udp_command(sock, command)
                last_command = command

            # Display command on the frame
            cv2.putText(frame, command, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Show the camera feed
            cv2.imshow("Robot Camera Feed", frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        sock.close()

# Run the robot control coroutine
asyncio.run(control_robot())
