# RC Car Controller with YOLO-based Human Detection

## Overview

This project provides a graphical user interface (GUI) for controlling an RC car using a Python-based application. It allows for both manual and automatic modes, where in manual mode, the user can control the car using keyboard inputs (`W`, `A`, `S`, `D`, `Q`, `E`), and in automatic mode, the car follows a detected human using a YOLO (You Only Look Once) object detection model.

## Features

- **Manual Mode**: 
  - Control the RC car using keyboard inputs:
    - `W` - Move Forward
    - `S` - Move Backward
    - `A` - Turn Left
    - `D` - Turn Right
    - `Q` - Stop
    - `E` - Exit application
- **Automatic Mode**: 
  - The car automatically follows a detected human using the YOLO model.
- **Video Feed Display**: 
  - The application displays a live video feed from the camera.
- **Toggle Mode**: 
  - Users can switch between manual and automatic modes using a toggle button.

## Prerequisites

### Hardware
- An RC car controlled by an ESP8266 microcontroller.
- A webcam or an IP camera for the video feed.

### Software
- Python 3.10
- Required Python packages:
  - `opencv-python`
  - `pillow`
  - `ultralytics`
  - `tkinter`
  - `asyncio`
- Trained YOLO model file (`yolo11n.pt`).

### Dependencies Installation

```bash
pip install opencv-python pillow ultralytics asyncio
```

## Setup

1. **Clone the repository**:
   ```bash
   git clone <git@github.com:Michael-Pio/AutomatedRemoteCar.git>
   cd <AutomatedRemoteCar>
   ```

2. **Update the server configuration**:
   - Modify the `UDP_IP` and `UDP_PORT` variables with your ESP8266 IP address and port:
     ```python
     UDP_IP = "192.168.139.135"  # Replace with your ESP8266 IP address
     UDP_PORT = 4210  # Replace with your port number
     ```

3. **Update the camera source**:
   - For a local webcam:
     ```python
     camUri = 0  # Default camera
     ```
   - For an IP camera, provide the URI:
     ```python
     camUri = r"http://<camera-ip>:<port>/videofeed"
     ```

4. **Place your trained YOLO model file (`yolo11n.pt`)** in the project directory.

## Usage

1. **Run the application**:
   ```bash
   python rc_car_controller.py
   ```

2. **Control the car**:
   - Use keyboard keys in manual mode:
     - Press `W`, `A`, `S`, `D` for movement commands.
     - Press `Q` to stop the car.
     - Press `E` to exit the application.
   - Toggle to automatic mode using the `Toggle Mode` button, and the car will follow a detected human.

## Key Functions

### Manual Mode Control
- **on_key_press(event)**: Handles the keyboard input for controlling the car.
- **send_command(direction, speed)**: Sends the movement command to the car via UDP.

### Automatic Mode Control
- **auto_control()**: Uses YOLO object detection to detect a human and sends movement commands based on the detected human's position.

### GUI and Video Feed
- **update_frame()**: Updates the video feed on the GUI.
- **toggle_mode()**: Switches between manual and automatic modes.

## Notes

- **Safety**: Ensure the RC car operates in a safe environment, especially in automatic mode, to prevent potential collisions or accidents.
- **Frame Processing**: The frame processing interval is set to 3 to reduce computational load. Adjust `process_frame_interval` for faster or slower response.
- **Command Interval**: The minimum interval between sending consecutive commands is set to 50 ms. Adjust `command_interval` if needed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The project utilizes the YOLO model for human detection, based on the [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) implementation.

## Troubleshooting

- **Camera Feed Issues**:
  - Ensure the camera URI is correct.
  - Check if the camera is accessible and not used by another application.
- **Connection Issues**:
  - Verify the IP address and port number of the ESP8266.
  - Ensure the UDP connection is not blocked by a firewall.
