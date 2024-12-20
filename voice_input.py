import pyaudio, wave, datetime, whisper, openai, time
import pvporcupine
import struct
import math 

'''
Get input from the microphone and append it to the prompt (which willl be used to generate code)
'''

# todo: can be replaced with only one button press

# https://github.com/Picovoice/porcupine 

porcupine = pvporcupine.create(
  access_key= 'ucYXcEspP3Lns+2XrcsUXMS6aKYv5dwpHxhrKMIXXIQEuiO6uLbe9w==',
  keyword_paths=['Hey-Obi_en_mac_v2_2_0.ppn'],
  sensitivities = [0.5]
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

with open('obi-prompt.txt', 'r') as f:
  file_contents = f.read()
# with open(LOG_FILE_PATH, 'w') as f:
#   f.write(f'System: {file_contents} \n\nTemp: {TEMPERATURE} \n\n\n')
messages = [{"role": "system", "content": file_contents}]

def sound_play_threading(sound):
    wave_obj = sa.WaveObject.from_wave_file(sound)
    play_obj = wave_obj.play()

def transcribe_audio(frames):
    ct = datetime.datetime.now()
    RECORDING_FILE_PATH = f"voice-recordings/{ct}.wav"
    print('Finished recording.')
    sound_file = "sounds_wav/processing.wav"
    sound_play_threading(sound_file)

    begin_time = time.time()

    # Save the recorded data as a WAV file
    wf = wave.open(RECORDING_FILE_PATH, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pa.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcribe the audio
    model = whisper.load_model("base.en")
    result = model.transcribe(RECORDING_FILE_PATH, fp16=False)["text"]
    elapsed_time = time.time() - begin_time
    print("Transcription Time: " + str(elapsed_time))
    print("Text: " + result)
    return result

if __name__ == "__main__":
    audio_stream.start_stream()
    data = audio_stream.read(1024)
    frames = []
    frames.append(data)
    audio_stream.stop_stream()
    #audio_stream.close()
    chatgpt_input = transcribe_audio(frames)
    # with open(LOG_FILE_PATH, 'a') as f:
    #     f.write(f'User: {chatgpt_input}\n\n\n')
    messages.append({"role": "user", "content": chatgpt_input})