import sys

import voice_input
import code_generation
import utils
import keyboard
from function_factory import TelloMovement
import tello


if __name__ == '__main__':
    while True:
        frames = voice_input.listen()

        if frames is None:
            print("Program ended by user.")
            sys.exit()

        voice_input.transcribe_audio(frames)
        api_key = utils.load_file('api_key.txt')
        messages = utils.load_file('command_prompt.txt')
        output_description = code_generation.get_chatgpt_code(messages, api_key)

        utils.speak(output_description)

        with open('code.txt', 'r') as f:
            code = f.read()

        print("Press the button once/'J' key to execute the code, press the button twice/'L' key to issue the command again.")

        execute_code = utils.execute_or_repeat()

        if execute_code:
            try:
                drone = TelloMovement(tello.Tello())
                drone.connect()
                exec(code, globals())

            except Exception as e:
                print(f"An error occurred: {str(e)}")
        else:
            continue



