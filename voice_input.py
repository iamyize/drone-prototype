import pyaudio, wave, datetime, openai, time
import pvporcupine
import struct
import math 
import simpleaudio as sa
import whisper

'''
Get input from the microphone and append it to the prompt (which willl be used to generate code)
'''

# todo: can be replaced with only one button press

# https://github.com/Picovoice/porcupine 

porcupine = pvporcupine.create(
  access_key= 'access key',
  keywords=['picovoice'],
  sensitivities = [0.5] # a higher sensitivity results in fewer misses at the cost of increasing the false alarm rate. the default is 0.5. 
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

with open('prompt.txt', 'r') as f:
  file_contents = f.read()
# with open(LOG_FILE_PATH, 'w') as f:
#   f.write(f'System: {file_contents} \n\nTemp: {TEMPERATURE} \n\n\n')
messages = [{"role": "system", "content": file_contents}]

def sound_play_threading(sound):
    wave_obj = sa.WaveObject.from_wave_file(sound)
    play_obj = wave_obj.play()

def transcribe_audio(frames):
    ct = datetime.datetime.now()
    RECORDING_FILE_PATH = f"{ct}.wav"
    print('Finished recording.')
    # sound_file = "sounds_wav/processing.wav"
    # sound_play_threading(sound_file)

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
    print('Listening...')
    
    try:
        while True:
            # returns the index of keyword detected, otherwise -1 if no keyword was detected. 
            data = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, data)
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                print("Wake word detected! Start recording ...")
          
                frames_per_second = int(fs)
                total_frames = frames_per_second * 5 # 5 seconds 
                chunk_size = 1024
                
                frames = []
                remaining_frames = total_frames
                
                while remaining_frames > 0:
                    frames_to_read = min(chunk_size, remaining_frames)
                    data = audio_stream.read(frames_to_read)
                    frames.append(data)
                    remaining_frames -= frames_to_read
          
                chatgpt_input = transcribe_audio(frames)
                messages.append({"role": "user", "content": chatgpt_input})
                print("Listening...")
                
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_stream.stop_stream()
        #audio_stream.close()
        pa.terminate()
        porcupine.delete()
