import base64

import pyaudio, wave, datetime, openai, time
import pvporcupine
import struct
import math

import requests
import simpleaudio as sa
import whisper
import utils
import os
import keyboard
from playsound import playsound
# from pynput import keyboard
'''
Get input from the microphone and append it to the prompt (which will be used to generate code)
'''

# todo: can be replaced with only one button press

# https://github.com/Picovoice/porcupine 

porcupine = pvporcupine.create(
  access_key= utils.load_file('picovoice_key.txt'),
  keywords=['computer', 'porcupine'], # just stupid examples
  sensitivities = [0.5, 0.5] # a higher sensitivity results in fewer misses at the cost of increasing the false alarm rate. the default is 0.5. 
)

pa = pyaudio.PyAudio()
channels = 1
sample_format = pyaudio.paInt16
mic_num = 0
fs = porcupine.sample_rate

audio_stream = pa.open(
    rate=fs,
    channels=channels,
    format=sample_format,
    input=True,
    frames_per_buffer=porcupine.frame_length,
    input_device_index=mic_num)

def rms(frame):
    count = len(frame)/2
    # short is 16 bit int
    shorts = struct.unpack("%dh" % count, frame)

    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768.0)
        sum_squares += n*n
    # compute the rms
    rms = math.pow(sum_squares/count, 0.5)
    return rms * 1000

def transcribe_audio(frames):
    # ct = datetime.datetime.now()
    # Reformat cos windows files cannot have ":"
    ct = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    RECORDING_FILE_PATH = f"audios/{ct}.wav"
    print('Finished recording.')



    # Save the recorded data as a WAV file
    os.makedirs(os.path.dirname(RECORDING_FILE_PATH), exist_ok=True)
    wf = wave.open(RECORDING_FILE_PATH, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pa.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcribe the audio
    google_key = utils.load_file('google_key.txt')
    google_url = f"https://speech.googleapis.com/v1/speech:recognize?key={google_key}"

    with open(RECORDING_FILE_PATH, "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode("utf-8")

    request = {
        "config": {
            "sampleRateHertz": 16000,
            "languageCode": "en-US"
        },
        "audio": {
            "content": audio_content
        }
    }

    begin_time = time.time()
    response = requests.post(google_url, json=request)

    if response.status_code != 200:
        print("Transcription API Error")
        return None

    result = response.json()["results"][0]["alternatives"][0]["transcript"]
    elapsed_time = time.time() - begin_time
    print("Transcription Time: " + str(elapsed_time))
    print("Text: " + result)

    with open('command_prompt.txt', 'w') as f:
        f.write(result)

    return result


def listen():
    frames = []

    try:
        print("Waiting for wake word. Say 'computer' to give a command, or say 'porcupine' to end the program.")
        audio_stream.start_stream()

        while True:
            data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, data)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                playsound('./resources/sounds/command_start_beep.wav')
                print("Started recording. Say 'porcupine' to stop recording.")
                break
            elif keyword_index == 1:
                if audio_stream.is_active():
                    audio_stream.stop_stream()
                audio_stream.close()
                pa.terminate()
                porcupine.delete()
                return None

        while True:
            data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            frames.append(data)
            pcm = struct.unpack_from("h" * porcupine.frame_length, data)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 1:
                # remove 2nd wake word frames, value is arbitrary for now
                frames = frames[:-(fs//porcupine.frame_length)]
                print("Wake word detected! Stopping recording...")
                break

    except KeyboardInterrupt:
        print("Stopping...")

    return frames
