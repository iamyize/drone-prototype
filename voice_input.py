import pyaudio, wave, datetime, openai, time
import pvporcupine
import struct
import math
import simpleaudio as sa
import whisper
import utils
import os
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

#with open('command_prompt.txt', 'r') as f:
  #file_contents = f.read()
# with open(LOG_FILE_PATH, 'w') as f:
#   f.write(f'System: {file_contents} \n\nTemp: {TEMPERATURE} \n\n\n')
#messages = [{"role": "system", "content": file_contents}]


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
    result = model.transcribe(RECORDING_FILE_PATH, fp16=False)["text"]
    elapsed_time = time.time() - begin_time
    print("Transcription Time: " + str(elapsed_time))
    print("Text: " + result)

    with open('command_prompt.txt', 'w') as f:
        f.write(result)

    return result


def listen():
    frames = []

    try:
        print('Waiting for first wake word to start recording...')
        audio_stream.start_stream()

        while True:
            data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, data)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                print("First wake word detected! Recording until next wake word...")
                break

        while True:
            data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            frames.append(data)
            pcm = struct.unpack_from("h" * porcupine.frame_length, data)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 1:
                # remove 2nd wake word frames, value is arbitrary for now
                frames = frames[:-(fs//porcupine.frame_length)]
                print("Second wake word detected! Stopping recording...")
                break

        # Process the recording
        # chatgpt_input = transcribe_audio(frames)
        #messages.append({"role": "user", "content": chatgpt_input})

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        if audio_stream.is_active():
            audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

    return frames

# if __name__ == "__main__":
#     try:
#         print('Waiting for first wake word to start recording...')
#         audio_stream.start_stream()
#         frames = []
#
#         while True:
#             data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
#             pcm = struct.unpack_from("h" * porcupine.frame_length, data)
#             keyword_index = porcupine.process(pcm)
#             if keyword_index == 0:
#                 print("First wake word detected! Recording until next wake word...")
#                 break
#
#         while True:
#             data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
#             frames.append(data)
#             pcm = struct.unpack_from("h" * porcupine.frame_length, data)
#             keyword_index = porcupine.process(pcm)
#             if keyword_index == 1:
#                 # remove 2nd wake word frames, value is arbitrary for now
#                 frames = frames[:-(fs//porcupine.frame_length)]
#                 print("Second wake word detected! Stopping recording...")
#                 break
#
#         # Process the recording
#         chatgpt_input = transcribe_audio(frames)
#         #messages.append({"role": "user", "content": chatgpt_input})
#
#     except KeyboardInterrupt:
#         print("Stopping...")
#     finally:
#         if audio_stream.is_active():
#             audio_stream.stop_stream()
#         audio_stream.close()
#         pa.terminate()
#         porcupine.delete()
