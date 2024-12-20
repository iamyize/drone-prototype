import openai
import time
import datetime

TEMPERATURE = 0.1
LOG_FILE_PATH = f"logs/{participantid}_{ct}.txt"

participantid = input("Enter the participant's ID: ")
ct = datetime.datetime.now()
    
def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()


def get_chatgpt_code(messages,api_key):
    try:
        begintime = time.time()
        client = openai.OpenAI(api_key=api_key)
        
        if isinstance(messages, str):
            messages = [
                {"role": "user", "content": messages}
            ]
        
        # send request 
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # todo: update model name
            temperature=TEMPERATURE,
            messages=messages
        )
    
        elapsedtime = time.time() - begintime
        output = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": output})
        print("ChatGPT: " + output)
        
        with open('code.txt', 'a') as f:
            f.write(output)

        with open(LOG_FILE_PATH, 'a') as f:
            f.write(f'ChatGPT Response Time: {elapsedtime}\nChatGPT: {output}\n\n\n')
        print("ChatGPT Response Time: " + str(elapsedtime))
   
    except openai.APIConnectionError as e:
        print(f"Connection error details: {str(e)}")
        raise
    except Exception as e:
        print(f"Other error occurred: {str(e)}")
        raise
    

if __name__ == "__main__":
    
    api_key = load_file('/Users/yize/GitHub/drone-prototype/api_key.txt')
    messages = load_file('/Users/yize/GitHub/drone-prototype/prompt.txt')
    get_chatgpt_code(messages,api_key)
    print("Generation Done!")

