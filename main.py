import sys

import voice_input
import code_generation
import utils
import keyboard
from function_factory import TelloMovement
import tello
import pprint
import datetime

api_key = utils.load_file('api_key.txt')
system_prompt = utils.load_file('original_prompt.txt')
messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]

participant_id = 1
ct = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE_PATH = f"logs/{participant_id}_{ct}.txt"
drone = TelloMovement(tello.Tello(), LOG_FILE_PATH)

if __name__ == '__main__':
    while True:
        frames = voice_input.listen()

        if frames is None:
            print("Program ended by user.")
            pprint.pprint(messages)
            sys.exit()

        command = voice_input.transcribe_audio(frames)
        output_description = code_generation.get_chatgpt_code(messages, command, log_file_path=LOG_FILE_PATH)

        if output_description is None:
            utils.speak("I couldn't catch that. Please try again.")
            continue
        else:
            utils.speak(output_description)

        code = utils.load_file('code.txt')

        print("Press the button once/'J' key to execute the code, press the button twice/'L' key to issue the command again.")

        execute_code = utils.execute_or_repeat()

        if execute_code:
            try:
                drone.connect()
                exec(code, globals())

            except Exception as e:
                print(f"An error occurred: {str(e)}")
        else:
            continue



