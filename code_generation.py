import openai
import time
import datetime
import utils
import os

# participantid = input("Enter the participant's ID: ")
participantid = 1
# ct = datetime.datetime.now()
# Reformat cos windows files cannot have ":"
ct = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
TEMPERATURE = 0.1
LOG_FILE_PATH = f"logs/{participantid}_{ct}.txt"


def get_chatgpt_code(messages, api_key):
    try:
        begintime = time.time()
        client = openai.OpenAI(api_key=api_key)

        developer_prompt = utils.load_file("original_prompt.txt")
        
        if isinstance(messages, str):
            messages = [
                {
                    "role": "developer",
                    "content": [{"type": "text", "text": developer_prompt}]
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": messages}]
                }
            ]
        
        # send request 
        completion = client.chat.completions.create(
            model="gpt-4o",  # todo: update model name
            temperature=TEMPERATURE,
            messages=messages
        )
    
        elapsedtime = time.time() - begintime
        output = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": output})

        parts = output.split("---")

        output_code = parts[0].strip()
        output_description = parts[1].strip()

        if "```" in output_code:
            output_code = output_code.split("```")[1]
            output_code = output_code.replace("python", "")

        output_code = '\n'.join(line for line in output_code.splitlines() if line.strip())

        print("ChatGPT:\n" + output_code)

        with open('code.txt', 'w') as f:
            f.write(output_code)

        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        with open(LOG_FILE_PATH, 'a') as f:
            f.write(f'ChatGPT Response Time: {elapsedtime}\nChatGPT: {output_code}\n\n\n')
        print("ChatGPT Response Time: " + str(elapsedtime))

        return output_description
   
    except openai.APIConnectionError as e:
        print(f"Connection error details: {str(e)}")
        raise
    except Exception as e:
        print(f"Other error occurred: {str(e)}")
        raise
