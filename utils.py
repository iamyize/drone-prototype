import time

import pyttsx3
import simpleaudio as sa
import keyboard
import importlib


def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()


def play_sound(sound):
    wave_obj = sa.WaveObject.from_wave_file(sound)
    play_obj = wave_obj.play()


def init_tts_engine():
    engine = pyttsx3.init()
    return engine


def speak(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()
    del engine


def start_command_or_exit(timeout):
    result = None

    def button_start_command(e):
        nonlocal result
        result = True

    def button_end_program(e):
        nonlocal result
        result = False

    keyboard.on_press_key("j", button_start_command, suppress=True)
    keyboard.on_press_key("l", button_end_program, suppress=True)

    button_timeout_start_time = time.time()

    while time.time() - button_timeout_start_time < timeout and result is None:
        time.sleep(0.01)

    keyboard.unhook_all()

    if result is not None:
        return result
    else:
        return False


def end_command():
    end_command = [False]

    def button_end_command(e):
        end_command[0] = True
        keyboard.unhook_all()

    keyboard.on_press_key("j", button_end_command, suppress=True)

    return end_command


def execute_or_repeat():
    while True:
        key = keyboard.read_key(suppress=True)

        if key == 'j':
            return True
        elif key == 'l':
            return False
