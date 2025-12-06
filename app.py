import os
import subprocess
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import webbrowser
import sys

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to say something and print it
def say(text):
    print(f"Speaking: {text}")  # Print what the assistant will say
    engine.say(text)
    engine.runAndWait()

# Function to get the current time
def current_time():
    now = datetime.now()
    return now.strftime("%I:%M %p")  # Format time in 12-hour format

# Function to show running applications (filter out system processes)
def show_running_apps():
    try:
        # Get the list of all running processes
        process_list = subprocess.check_output(['ps', 'aux']).decode('utf-8').splitlines()
        running_apps = []

        # Process the output and filter for applications (ignoring system processes)
        for line in process_list:
            parts = line.split()
            if len(parts) > 10:  # Ensure there are enough parts
                app_name = parts[10]  # Application name usually appears at index 10
                # Filter out kernel processes and system services
                if app_name not in running_apps and app_name not in ["ps", "init", "systemd"]:
                    running_apps.append(app_name)

        # Join all unique app names into a single string for output
        app_list = "\n".join(running_apps)
        
        # Print the list in the terminal
        print(f"Currently running applications:\n{app_list}")

    except Exception as e:
        say(f"Error retrieving running applications: {str(e)}")

# Function to close an application by name
def close_application(app_name):
    try:
        # Check if the app is running first
        process_list = subprocess.check_output(['ps', 'aux']).decode('utf-8').splitlines()
        running_apps = [line.split()[10] for line in process_list if len(line.split()) > 10]
        
        if app_name in running_apps:
            subprocess.call(['pkill', app_name])  # Use pkill to terminate the application by name
            print(f"Closing {app_name}...")  # Log the action in the terminal
        else:
            print(f"{app_name} is not currently running.")  # Log the error in the terminal
    except Exception as e:
        print(f"Error closing {app_name}: {str(e)}")

# Shutdown system
def shutdown_system():
    subprocess.call(['shutdown', '-h', 'now'])

# Reboot system
def reboot_system():
    subprocess.call(['reboot'])

# Exit the program
def exit_program():
    sys.exit(0)

# Open Google
def open_google():
    webbrowser.open('https://www.google.com')

# Open YouTube
def open_youtube():
    webbrowser.open('https://www.youtube.com')

# Open Terminal
def open_terminal():
    subprocess.Popen(['konsole'])

# Function to run Flatpak applications
def run_flatpak_app(app_name):
    try:
        # First, search for the application in Flatpak
        say(f"Searching for {app_name}...")
        
        # Search for installed Flatpak applications
        search_result = subprocess.check_output(['flatpak', 'list', '--app'], text=True, stderr=subprocess.STDOUT)
        
        # Search for the app name in the list (case-insensitive)
        matching_apps = []
        for line in search_result.split('\n'):
            if app_name.lower() in line.lower():
                matching_apps.append(line)
        
        if matching_apps:
            # If we found matches, try to run the first one
            # Extract the application ID from the first match
            app_info = matching_apps[0].split('\t')
            if len(app_info) >= 2:
                app_id = app_info[1]  # Application ID is usually in the second column
                say(f"Found {app_name}. Launching it now...")
                print(f"Launching Flatpak app: {app_id}")
                
                # Run the Flatpak application in a separate process that doesn't inherit the terminal
                # Use Popen with detach flags to run it in the background
                subprocess.Popen(['flatpak', 'run', app_id],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,
                                 start_new_session=True)
                return
        
        # If no exact match found, try to run with the name directly
        say(f"Launching {app_name}...")
        print(f"Attempting to launch: {app_name}")
        
        # Try to run the app directly in the background
        try:
            subprocess.Popen([app_name.lower()],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
        except:
            # If that fails, try to run it as a Flatpak app in the background
            subprocess.Popen(['flatpak', 'run', app_name],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Error searching for Flatpak apps: {e.output}"
        say(error_msg)
        print(error_msg)
    except FileNotFoundError:
        error_msg = "Flatpak is not installed or not in PATH."
        say(error_msg)
        print(error_msg)
    except Exception as e:
        error_msg = f"Error running {app_name}: {str(e)}"
        say(error_msg)
        print(error_msg)

# Function to close a Flatpak application
def close_flatpak_app(app_name):
    try:
        # Common app mappings to Flatpak IDs
        app_mappings = {
            'sober': 'org.vinegarhq.Sober',
            'chrome': 'com.google.Chrome',
            'firefox': 'org.mozilla.firefox',
            'gimp': 'org.gimp.GIMP',
            'roblox': 'org.vinegarhq.Sober'
        }
        
        # Get the Flatpak ID
        app_name_lower = app_name.lower()
        if app_name_lower in app_mappings:
            flatpak_id = app_mappings[app_name_lower]
            print(f"Closing Flatpak app: {flatpak_id}")
            
            # Try to close using flatpak kill
            try:
                subprocess.run(['flatpak', 'kill', flatpak_id], 
                             check=True, capture_output=True, text=True)
                say(f"Closed {app_name}")
                return
            except subprocess.CalledProcessError:
                # If flatpak kill fails, try pkill with the app name
                pass
        
        # Try to find and close by process name
        try:
            # Search for the app process
            ps_output = subprocess.check_output(['ps', 'aux'], text=True)
            
            # Look for processes related to the app
            for line in ps_output.split('\n'):
                if app_name_lower in line.lower():
                    # Try to extract PID and kill it
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        subprocess.run(['kill', '-9', pid], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            say(f"Closed {app_name}")
            
        except Exception as e:
            say(f"Could not close {app_name}. It might not be running.")
            print(f"Error closing {app_name}: {e}")
            
    except Exception as e:
        error_msg = f"Error closing {app_name}: {str(e)}"
        say(error_msg)
        print(error_msg)

# Function to load commands from the commands.txt file
def load_commands():
    commands = []
    try:
        with open("commands.txt", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    command_name = parts[0].strip()
                    response = parts[1].strip().strip('"')
                    function_call = parts[2].strip()
                    commands.append((command_name, response, function_call))
    except FileNotFoundError:
        print("commands.txt file not found.")
    return commands

# Function to execute the dynamic command
def execute_command(command, response, function_call):
    # For time command, we need to get the time and append it to the response
    if function_call == "current_time()":
        time_str = current_time()
        say(f"{response}{time_str}")
        return
    
    # For other commands, just say the response
    if response:
        say(response)
    
    # Dynamically execute the function using globals()
    try:
        # If the function call has arguments, extract and pass them
        if '(' in function_call and ')' in function_call:
            func_name = function_call.split('(')[0].strip()
            args_str = function_call.split('(')[1].split(')')[0].strip()
            
            if args_str:
                # For commands like "close <app_name>" or "run <app_name>"
                if '<' in args_str and '>' in args_str:
                    # Extract the placeholder name
                    placeholder = args_str.strip('<>')
                    # Try to extract the actual value from the command
                    # Example: command "run firefox", extract "firefox"
                    cmd_parts = command.split()
                    if len(cmd_parts) > 1:
                        actual_arg = ' '.join(cmd_parts[1:])  # Everything after command name
                        func = globals()[func_name]
                        func(actual_arg)
                    else:
                        print(f"No argument provided for {func_name}")
                else:
                    # Regular arguments
                    args = tuple(arg.strip() for arg in args_str.split(','))
                    func = globals()[func_name]
                    func(*args)
            else:
                # No arguments
                func = globals()[func_name]
                func()
        else:
            # No parentheses, just function name
            func = globals()[function_call]
            func()

    except Exception as e:
        print(f"Error executing function '{function_call}': {e}")

# Voice input function to listen for commands - waits for natural speech end
def voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    # Configure the recognizer for continuous listening
    recognizer.pause_threshold = 0.8  # Wait 0.8 seconds of silence to consider speech ended
    recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking before considering it speech
    recognizer.non_speaking_duration = 0.5  # Seconds of non-speaking before considering phrase complete
    
    print("🎤 Always listening... say 'assistant' then your command")
    
    while True:
        try:
            with mic as source:
                # Adjust for ambient noise once
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen with no timeout - waits for natural speech end
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
            
            # Process what was said
            command = recognizer.recognize_google(audio).lower()
            
            # Check if it starts with "assistant"
            if command.startswith("assistant"):
                print(f"✅ Command received: assistant {command.replace('assistant', '', 1).strip()}")
                actual_command = command.replace("assistant", "", 1).strip()
                
                if actual_command:
                    return actual_command
                else:
                    # Just "assistant" was said
                    say("Yes? What would you like me to do?")
                    continue
            else:
                # Not for me, ignore COMPLETELY (no print)
                continue
                
        except sr.UnknownValueError:
            # This happens when there's noise but no clear speech
            # Just continue listening silently
            continue
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            say("Having trouble with speech recognition.")
            return None
        except Exception as e:
            # Don't print other errors either
            continue

# Keyboard input function to accept typed commands
def keyboard_input():
    print("Type a command (type 'exit' to quit):")
    command = input()
    return command.lower()

# Main function to handle commands
def main(input_mode):
    # Load commands from the commands.txt file
    commands = load_commands()
    
    if not commands:
        print("No valid commands found in commands.txt.")
        return
    
    while True:
        if input_mode == "voice":
            command = voice_input()  # This now returns just the command part after "assistant"
        elif input_mode == "keyboard":
            command = keyboard_input()
        else:
            print("Usage: python3 app.py voice or python3 app.py keyboard")
            break
        
        if command:
            # Check if the command exists in the loaded commands
            command_matched = False
            for cmd, response, function_call in commands:
                # Special handling for commands with placeholders like "run <app_name>"
                if '<' in cmd and '>' in cmd:
                    # Extract the base command (e.g., "run" from "run <app_name>")
                    base_cmd = cmd.split('<')[0].strip()
                    # Check if the command starts with the base command
                    if command.startswith(base_cmd):
                        execute_command(command, response, function_call)
                        command_matched = True
                        # If it's an exit command, we're done
                        if cmd == "exit":
                            return
                        break
                else:
                    # For regular commands without placeholders
                    if cmd in command:
                        execute_command(command, response, function_call)
                        command_matched = True
                        # If it's an exit command, we're done
                        if cmd == "exit":
                            return
                        break
            
            if not command_matched:
                say(f"Command '{command}' not recognized.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 app.py voice or python3 app.py keyboard")
    else:
        input_mode = sys.argv[1].lower()
        try:
            main(input_mode)
        except KeyboardInterrupt:
            say("Exiting the program.")
        except SystemExit:
            # Let the system exit normally
            pass