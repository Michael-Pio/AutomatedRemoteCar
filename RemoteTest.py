import asyncio
import websockets
import json
import keyboard  # Use the keyboard module for capturing key presses

async def send_command(websocket, direction, speed=75):
    # Send JSON-encoded command to the WebSocket
    command = json.dumps({"direction": direction, "speed": speed})
    await websocket.send(command)
    print(f"Sent: {command}")

async def main():
    uri = "ws://192.168.165.135:81"  # Replace with the IP address of your ESP8266
    print("Use W/A/S/D to control the car, Q to stop, and E to exit.")

    # Establish a single WebSocket connection
    async with websockets.connect(uri) as websocket:
        try:
            while True:
                # Check for keyboard input and send corresponding commands
                if keyboard.is_pressed('w'):
                    await send_command(websocket, "FWD", 75)
                elif keyboard.is_pressed('s'):
                    await send_command(websocket, "BWD", 75)
                elif keyboard.is_pressed('a'):
                    await send_command(websocket, "LFT", 75)
                elif keyboard.is_pressed('d'):
                    await send_command(websocket, "RGT", 75)
                elif keyboard.is_pressed('q'):
                    await send_command(websocket, "STP", 0)
                elif keyboard.is_pressed('e'):
                    print("Exiting...")
                    break
                
                await asyncio.sleep(0.1)  # Short delay to prevent flooding
        except websockets.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")

# Run the main function
asyncio.run(main())
