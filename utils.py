import pyttsx3
import simpleaudio as sa


def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()


def play_sound(sound):
    wave_obj = sa.WaveObject.from_wave_file(sound)
    play_obj = wave_obj.play()


def init_tts_engine():
    engine = pyttsx3.init()
    return engine


def speak(engine, message):
    engine.say(message)
    engine.runAndWait()
