import os
import subprocess
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import webbrowser
import sys
import requests
import time
import threading
from pynput.mouse import Controller, Button

global_commands = []

autoclicker_clicking = False
autoclicker_click_count = 0
autoclicker_session_start = 0
mouse_controller = Controller()
autoclicker_thread = None



engine = pyttsx3.init()

def say(text):
    """Speak text using TTS"""
    print(f"Speaking:  {text}")
    engine.say(text)
    engine.runAndWait()

def current_time():
    now = datetime.now()
    return now.strftime("%I:%M %p")

def show_running_apps():
    try:
        process_list = subprocess.check_output(['ps', 'aux']).decode('utf-8').splitlines()
        running_apps = []
        for line in process_list:
            parts = line.split()
            if len(parts) > 10:
                app_name = parts[10]
                if app_name not in running_apps and app_name not in ["ps", "init", "systemd"]:
                    running_apps.append(app_name)
        app_list = "\n".join(running_apps)
        print(f"Currently running applications:\n{app_list}")
    except Exception as e:
        say(f"Error retrieving running applications: {str(e)}")

def close_application(app_name):
    try:
        process_list = subprocess.check_output(['ps', 'aux']).decode('utf-8').splitlines()
        matching_pids = []
        app_processes = []
        for line in process_list:
            parts = line.split()
            if len(parts) > 10:
                process_name = parts[10]
                if app_name.lower() in process_name.lower() or app_name.lower() in line.lower():
                    pid = parts[1]
                    matching_pids.append(pid)
                    app_processes.append(process_name)
        if matching_pids:
            for pid in matching_pids:
                try:
                    subprocess.call(['kill', '-9', pid])
                except:
                    pass
            if app_processes:
                unique_apps = list(set(app_processes))
                app_list = ", ".join(unique_apps[:3])
                if len(unique_apps) > 3:
                    app_list += "..."
                say(f"Closed {app_list}")
            else:
                say(f"Closed {app_name}")
            print(f"Closed {app_name} (PID(s): {', '.join(matching_pids)})")
        else:
            say(f"{app_name} is not currently running.")
            print(f"{app_name} is not currently running.")
    except Exception as e:
        say(f"Error closing {app_name}: {str(e)}")
        print(f"Error closing {app_name}: {str(e)}")

def shutdown_system():
    subprocess.call(['shutdown', '-h', 'now'])

def reboot_system():
    subprocess.call(['reboot'])

def exit_program():
    sys.exit(0)

def open_google():
    webbrowser.open('https://www.google.com')

def open_youtube():
    webbrowser.open('https://www.youtube.com')

def open_whatsapp():
    webbrowser.open('https://web.whatsapp.com')

def open_momlang():
    webbrowser.open('https://momlang.vercel.app')

def open_terminal():
    subprocess.Popen(['konsole'])

def open_file_explorer():
    subprocess.Popen(['dolphin'])

def run_flatpak_app(app_name):
    try:
        say(f"Searching for {app_name}...")
        search_result = subprocess.check_output(['flatpak', 'list', '--app'], text=True, stderr=subprocess.STDOUT)
        matching_apps = []
        for line in search_result.split('\n'):
            if app_name.lower() in line.lower():
                matching_apps.append(line)
        if matching_apps:
            app_info = matching_apps[0].split('\t')
            if len(app_info) >= 2:
                app_id = app_info[1]
                say(f"Found {app_name}. Launching it now...")
                print(f"Launching Flatpak app: {app_id}")
                subprocess.Popen(['flatpak', 'run', app_id],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)
                return
        say(f"Launching {app_name}...")
        print(f"Attempting to launch: {app_name}")
        try:
            subprocess.Popen([app_name.lower()],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
        except:
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

def close_flatpak_app(app_name):
    try:
        app_mappings = {
            'sober': 'org.vinegarhq.Sober',
            'chrome': 'com.google.Chrome',
            'firefox': 'org.mozilla.firefox',
            'gimp': 'org.gimp.GIMP',
            'roblox': 'org.vinegarhq.Sober'
        }
        app_name_lower = app_name.lower()
        if app_name_lower in app_mappings:
            flatpak_id = app_mappings[app_name_lower]
            print(f"Closing Flatpak app: {flatpak_id}")
            try:
                subprocess.run(['flatpak', 'kill', flatpak_id],
                             check=True, capture_output=True, text=True)
                say(f"Closed {app_name}")
                return
            except subprocess.CalledProcessError:
                pass
        try:
            ps_output = subprocess.check_output(['ps', 'aux'], text=True)
            for line in ps_output.split('\n'):
                if app_name_lower in line.lower():
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

def close_app(app_name):
    try:
        close_flatpak_app(app_name)
        return
    except:
        pass
    try:
        close_application(app_name)
        return
    except Exception as e:
        say(f"Could not close {app_name}")
        print(f"Error closing {app_name}: {e}")

def reload():
    global global_commands
    commands = load_commands()
    if commands:
        say(f"Successfully reloaded {len(commands)} commands.")
    else:
        say("Failed to reload commands.")

def get_weather(city=""):
    """
    Get weather without any API key using wttr.in
    Usage: 
    - "weather" (gets weather for your location)
    - "weather london" (gets weather for London)
    - "weather new york" (gets weather for New York)
    """
    try:

        if city and ' ' in city:
            city = city.replace(' ', '+')
        

        url = f"http://wttr.in/{city}?format=%l:%C+%t+Humidity+%h+Wind+%w"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather_data = response.text.strip()
            

            weather_data = weather_data.replace('°C', ' degrees celsius')
            weather_data = weather_data.replace('°F', ' degrees fahrenheit')
            weather_data = weather_data.replace('km/h', ' kilometers per hour')
            weather_data = weather_data.replace('m/s', ' meters per second')
            
            say(weather_data)
        else:
            if city:
                say(f"Could not get weather for {city}")
            else:
                say("Could not get weather information")
                
    except requests.exceptions.ConnectionError:
        say("No internet connection for weather service")
    except requests.exceptions.Timeout:
        say("Weather service is taking too long to respond")
    except Exception as e:
        say("Unable to get weather information at the moment")


def run_autoclicker():
    """Toggle autoclicker on/off"""
    global autoclicker_clicking, autoclicker_click_count, autoclicker_session_start, autoclicker_thread, mouse_controller
    
    def autoclicker_click_loop():
        global autoclicker_clicking, autoclicker_click_count, autoclicker_session_start
        local_count = 0
        last_display = time.time()
        
        try:
            while autoclicker_clicking:

                mouse_controller.click(Button.left)
                local_count += 1
                autoclicker_click_count += 1
                

                current = time.time()
                if current - last_display > 0.2:
                    elapsed = current - autoclicker_session_start
                    cps = autoclicker_click_count / elapsed if elapsed > 0 else 0
                    print(f"\r✅ Autoclicker: {autoclicker_click_count:,} clicks | {cps:.0f}/sec", end="", flush=True)
                    last_display = current
                

                time.sleep(0.001)
                
        except Exception as e:
            print(f"\n❌ Autoclicker Error: {e}")
    
    if not autoclicker_clicking:

        autoclicker_clicking = True
        autoclicker_click_count = 0
        autoclicker_session_start = time.time()
        

        autoclicker_thread = threading.Thread(target=autoclicker_click_loop, daemon=True)
        autoclicker_thread.start()
        
        print("\n▶ Autoclicker Started!")
        say("Autoclicker activated!")
    else:

        autoclicker_clicking = False
        

        elapsed = time.time() - autoclicker_session_start
        if elapsed > 0 and autoclicker_click_count > 0:
            cps = autoclicker_click_count / elapsed
            stats = f"Autoclicker stopped. Made {autoclicker_click_count:,} clicks at {cps:.0f} clicks per second."
            print(f"\n📊 {stats}")
            say(stats)
        else:
            say("Autoclicker deactivated.")
        
        time.sleep(0.1) 

def autoclicker_status():
    """Check autoclicker status"""
    global autoclicker_clicking, autoclicker_click_count, autoclicker_session_start
    
    if autoclicker_clicking:
        elapsed = time.time() - autoclicker_session_start
        cps = autoclicker_click_count / elapsed if elapsed > 0 else 0
        status_msg = f"Autoclicker is active. {autoclicker_click_count:,} clicks made at {cps:.0f} clicks per second."
        print(f"Status: {status_msg}")
        say(status_msg)
    else:
        say("Autoclicker is not running.")

def load_commands():
    global global_commands
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
        global_commands = commands
        print(f"Loaded {len(commands)} commands from commands.txt")
        return commands
    except FileNotFoundError:
        print("commands.txt file not found.")
        return []

def execute_command(command, response, function_call):
    if function_call == "current_time()":
        time_str = current_time()
        say(f"{response}{time_str}")
        return
    if response:
        say(response)
    try:
        if '(' in function_call and ')' in function_call:
            func_name = function_call.split('(')[0].strip()
            args_str = function_call.split('(')[1].split(')')[0].strip()
            if args_str:
                if '<' in args_str and '>' in args_str:
                    placeholder = args_str.strip('<>')
                    cmd_parts = command.split()
                    if len(cmd_parts) > 1:
                        actual_arg = ' '.join(cmd_parts[1:])
                        func = globals()[func_name]
                        func(actual_arg)
                    else:
                        print(f"No argument provided for {func_name}")
                else:
                    args = tuple(arg.strip() for arg in args_str.split(','))
                    func = globals()[func_name]
                    func(*args)
            else:
                func = globals()[func_name]
                func()
        else:
            func = globals()[function_call]
            func()
    except Exception as e:
        print(f"Error executing function '{function_call}': {e}")

def voice_input():
    """Original responsive voice input function"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    

    recognizer.pause_threshold = 0.8      
    recognizer.phrase_threshold = 0.3    
    recognizer.non_speaking_duration = 0.5  
    
    print("🎤 Always listening... say 'assistant' then your command")
    
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        while True:
            try:

                audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
                command = recognizer.recognize_google(audio).lower()
                
                if command.startswith("assistant"):
                    print(f"✅ Command received: assistant {command.replace('assistant', '', 1).strip()}")
                    actual_command = command.replace("assistant", "", 1).strip()
                    
                    if actual_command:
                        return actual_command
                    else:
                        say("Yes? What would you like me to do?")
                        continue
                else:
                    continue
                    
            except sr.UnknownValueError:

                continue
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                say("Having trouble with speech recognition.")
                return None
            except Exception as e:

                continue

def keyboard_input():
    print("Type a command (type 'exit' to quit):")
    command = input()
    return command.lower()

def match_command(user_input, commands):
    """Match user input with available commands"""
    user_input = user_input.lower()
    

    for cmd, response, func in commands:
        if cmd.lower() == user_input:
            return cmd, response, func
    

    for cmd, response, func in commands:
        if '<' in cmd and '>' in cmd:
            base_cmd = cmd.split('<')[0].strip().lower()
            if user_input.startswith(base_cmd):
                return cmd, response, func
    

    for cmd, response, func in commands:
        if cmd.lower() in user_input:
            return cmd, response, func
    
    return None, None, None

def main(input_mode):
    load_commands()
    if not global_commands:
        print("No valid commands found in commands.txt.")
        return
    
    while True:
        if input_mode == "voice":
            command = voice_input()
        elif input_mode == "keyboard":
            command = keyboard_input()
        else:
            print("Usage: python3 app.py voice 2>/dev/null or python3 app.py keyboard")
            break
        
        if command:

            cmd, response, func = match_command(command, global_commands)
            
            if cmd:
                execute_command(command, response, func)
                if cmd == "exit":
                    return
            else:
                say(f"Command '{command}' not recognized.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 app.py voice 2>/dev/null or python3 app.py keyboard")
    else:
        input_mode = sys.argv[1].lower()
        try:
            main(input_mode)
        except KeyboardInterrupt:
            say("Exiting the program.")
        except SystemExit:
            pass
