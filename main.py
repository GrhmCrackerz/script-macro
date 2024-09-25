from pynput import mouse, keyboard
import time
import json
import os

actions = []
recording = True
stop_listeners = False  # Global flag to stop both listeners
input_buffer = ""  # Buffer to store typed keys for detecting "end"


def on_click(x, y, button, pressed):
    global stop_listeners
    if stop_listeners:
        return False  # Stop the mouse listener
    if recording:
        actions.append(('mouse', time.time(), x, y, button.name, pressed))


def on_press(key):
    global recording, stop_listeners, input_buffer
    if recording:
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
            actions.append(('keyboard', time.time(), key_name, 'press'))
            # Check if the key pressed is a character and append it to the buffer
            if hasattr(key, 'char'):
                input_buffer += key.char
                # If "end" is typed, stop recording
                if "end" in input_buffer:
                    print("End command received. Stopping recording.")
                    recording = False
                    stop_listeners = True
                    return False  # Stop the keyboard listener
            # Limit the buffer size to avoid it growing too large
            input_buffer = input_buffer[-10:]
        except AttributeError:
            pass


def on_release(key):
    if recording:
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
            actions.append(('keyboard', time.time(), key_name, 'release'))
        except AttributeError:
            actions.append(('keyboard', time.time(), str(key), 'release'))


def record_actions():
    global recording
    print("Recording started. Type 'end' to stop recording.")

    # Set up the mouse and keyboard listeners
    with mouse.Listener(on_click=on_click) as mouse_listener, \
            keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
        keyboard_listener.join()
        mouse_listener.join()

    print("Recording stopped.")


def save_log():
    # Define the file path on the desktop
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    log_file = os.path.join(desktop, "actions_log.json")

    with open(log_file, "w") as file:
        json.dump(actions, file, indent=4, default=str)
    print(f"Action log saved to {log_file}")


if __name__ == "__main__":
    record_actions()
    save_log()
