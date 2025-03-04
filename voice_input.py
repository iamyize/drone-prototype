import pyaudio, wave, datetime, openai, time
import pvporcupine
import struct
import math
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
  keywords=['picovoice', 'grapefruit'], # just stupid examples 
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

    begin_time = time.time()

    # Save the recorded data as a WAV file
    os.makedirs(os.path.dirname(RECORDING_FILE_PATH), exist_ok=True)
    wf = wave.open(RECORDING_FILE_PATH, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pa.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcribe the audio
    model = whisper.load_model("base.en")
    print(f"Audio file path: {RECORDING_FILE_PATH}")
    result = model.transcribe(RECORDING_FILE_PATH, fp16=False)["text"]
    elapsed_time = time.time() - begin_time
    print("Transcription Time: " + str(elapsed_time))
    print("Text:" + result)

    with open('command_prompt.txt', 'w') as f:
        f.write(result)

    return result


def listen():
    frames = []

    button_timeout = 30

    try:
        print("Press the button once/'J' key when ready to give command, press the button twice/'L' key to end the program.")

        start_command = utils.start_command_or_exit(timeout=button_timeout)

        if not start_command:
            if audio_stream.is_active():
                audio_stream.stop_stream()
            audio_stream.close()
            pa.terminate()
            return None

        time.sleep(0.5)
        audio_stream.start_stream()
        playsound('./resources/sounds/command_start_beep.wav')
        print("Started recording. Press the button once/'J' key to stop recording.")

        end_command = utils.end_command()

        while not end_command[0]:
            data = audio_stream.read(1024)
            frames.append(data)
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping...")

    return frames
