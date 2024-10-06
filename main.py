import pynput
import pyautogui
import time
import threading

# Global variables for recording and control
recording = False
actions_log = []
command = ""

# Lock for thread-safe access to shared variables
lock = threading.Lock()


# Function to capture keyboard events
def on_keyboard_event(key):
    with lock:
        if recording:
            try:
                actions_log.append(('key_press', key.char, time.time()))
            except AttributeError:
                actions_log.append(('key_press', str(key), time.time()))


# Function to capture mouse events
def on_click(x, y, button, pressed):
    with lock:
        if recording and pressed:
            actions_log.append(('mouse_click', (x, y, button), time.time()))


# Function to start recording input events
def start_recording():
    global recording, actions_log
    with lock:
        recording = True
        actions_log = []
    print("Recording started...")


# Function to stop recording input events
def stop_recording():
    global recording
    with lock:
        recording = False
    print("Recording stopped.")


# Function to print the recorded log
def print_log():
    with lock:
        for action in actions_log:
            print(action)


# Function to replay recorded actions
def replay_actions():
    with lock:
        if not actions_log:
            print("No actions recorded.")
            return
        # Calculate time differences between actions
        initial_time = actions_log[0][2]
        for action in actions_log:
            action_type, action_detail, timestamp = action
            time.sleep(timestamp - initial_time)
            initial_time = timestamp

            if action_type == 'key_press':
                if len(action_detail) == 1:  # Single character
                    pyautogui.press(action_detail)
                else:
                    print(f"Unrecognized key: {action_detail}")

            elif action_type == 'mouse_click':
                x, y, button = action_detail
                pyautogui.click(x, y)

    print("Action replay complete.")


# Command interface for user inputs
def command_interface():
    global command
    print("Command Interface Started. Enter commands: start, stop, print, replay, or exit.")
    while command.lower() != 'exit':
        command = input("Enter command: ").lower()
        if command == "start":
            start_recording()
        elif command == "stop":
            stop_recording()
        elif command == "print":
            print_log()
        elif command == "replay":
            replay_actions()
        elif command == "exit":
            print("Exiting script...")
        else:
            print(f"Unknown command: {command}")


# Start listeners in separate threads
keyboard_listener = pynput.keyboard.Listener(on_press=on_keyboard_event)
mouse_listener = pynput.mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

# Run the command interface in the main thread
command_interface()

# Stop listeners after exiting
keyboard_listener.stop()
mouse_listener.stop()
