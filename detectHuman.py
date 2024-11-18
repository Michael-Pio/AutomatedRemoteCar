from ultralytics import YOLO
import cv2

# Load the YOLO model trained to detect humans
model = YOLO("yolo11n.pt") 

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
center_x = frame_width // 2
tolerance = 50  

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    results = model(frame)

    human_detected = None
    for detection in results[0].boxes:
        if detection.cls == 0:
            human_detected = detection
            break

    # Determine movement commands based on human position
    if human_detected:
        x_min, y_min, x_max, y_max = human_detected.xyxy[0]
        human_center_x = (x_min + x_max) // 2  # Calculate horizontal center of detected human

        # Check the position of the detected human relative to the frame center
        if human_center_x < center_x - tolerance:
            command = "Turn Left"
        elif human_center_x > center_x + tolerance:
            command = "Turn Right"
        else:
            command = "Go Straight"
            
        cv2.putText(frame, command, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        print(command)  # Or send command to control the robot

    # Display the resulting frame
    cv2.imshow("Robot Camera Feed", frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
