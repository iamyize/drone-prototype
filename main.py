import sys

import voice_input
import code_generation
import utils
from function_factory import TelloMovement
import tello


if __name__ == '__main__':
    frames = voice_input.listen()
    voice_input.transcribe_audio(frames)

    api_key = utils.load_file('api_key.txt')
    messages = utils.load_file('command_prompt.txt')
    code_generation.get_chatgpt_code(messages, api_key)
    print("Generation Done!")

    with open('code.txt', 'r') as f:
        code = f.read()

    flag = input("To exit, enter 0. To execute code, enter 1:")

    if flag == '0':
        sys.exit()

    elif flag == '1':
        try:
            drone = TelloMovement(tello.Tello())
            drone.connect()
            exec(code, globals())

        except Exception as e:
            print(f"An error occurred: {str(e)}")

