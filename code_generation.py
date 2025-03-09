import openai
import time
import datetime
import utils
import os

# participantid = input("Enter the participant's ID: ")
# participantid = 1
# ct = datetime.datetime.now()
# Reformat cos windows files cannot have ":"
# ct = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
# TEMPERATURE = 0.1
# LOG_FILE_PATH = f"logs/{participantid}_{ct}.txt"
client = openai.OpenAI(api_key=utils.load_file('api_key.txt'))


def verify_code(code):
    if "drone.find_item" in code:
        code = '\n'.join(line for line in code.splitlines() if any(word in line.lower() for word in ["take_off", "land", "find_item"]))
    elif "ask_color" in code:
        code = '\n'.join(line for line in code.splitlines() if ("ask_color" in line.lower()))
    elif "count" in code:
        code = '\n'.join(line for line in code.splitlines() if ("count" in line.lower()))
    elif "ask" in code:
        code = '\n'.join(line for line in code.splitlines() if ("ask" in line.lower()))
    elif "where_am_i" in code:
        code = '\n'.join(line for line in code.splitlines() if any(word in line.lower() for word in ["take_off", "land", "where_am_i"]))

    return code


def get_chatgpt_code(messages, command, log_file_path):
    try:
        begin_time = time.time()
        
        if isinstance(command, str):
            messages.append({"role": "user", "content": command})
        
        # send request 
        completion = client.chat.completions.create(
            model="gpt-4o",  # todo: update model name
            messages=messages
        )
    
        elapsed_time = time.time() - begin_time
        output = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": output})

        if "---" not in output:
            return None

        parts = output.split("---")

        output_code = parts[0].strip()
        output_description = parts[1].strip()

        if "```" in output_code:
            output_code = output_code.split("```")[1]
            output_code = output_code.replace("python", "")

        output_code = '\n'.join(line for line in output_code.splitlines() if line.strip())
        verified_code = verify_code(output_code)

        print("ChatGPT:\n" + verified_code)

        with open('code.txt', 'w') as f:
            f.write(verified_code)

        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        with open(log_file_path, 'a') as f:
            f.write(f'User:{command}\nResponse Time: {elapsed_time}\nChatGPT:\n{verified_code}\n\n\n')
        print("ChatGPT Response Time: " + str(elapsed_time))

        return output_description
   
    except openai.APIConnectionError as e:
        print(f"Connection error details: {str(e)}")
        raise
    except Exception as e:
        print(f"Other error occurred: {str(e)}")
        raise
