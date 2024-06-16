from djitellopy import Tello
import keyboard_module as kb
import time
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import cv2

load_dotenv()
kb.init()

client = OpenAI()

def save_and_generate_description(image):
    Path("resources/images").mkdir(parents=True, exist_ok=True)

    image_path = f"resources/images/{time.time()}.jpg"

    cv2.imwrite(image_path, img)

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = "Identify and describe all objects in the image. Also estimate the distance between the camera and the object directly ahead."

    image_description = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    response = image_description.choices[0].message.content

    file = open("resources/chat.txt", "w")
    file.write(".\n".join(response.split(". ")))
    file.close()


drone = Tello(response_timeout=10)
drone.connect()
print(drone.get_battery())
global img
drone.streamon()


def get_keyboard_input():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kb.getKey("LEFT"):
        lr = -speed
    elif kb.getKey("RIGHT"):
        lr = speed

    if kb.getKey("UP"):
        fb = speed
    elif kb.getKey("DOWN"):
        fb = -speed

    if kb.getKey("w"):
        ud = speed
    elif kb.getKey("s"):
        yv = -speed

    if kb.getKey("a"):
        yv = speed
    elif kb.getKey("d"):
        yv = -speed

    if kb.getKey("q"): drone.land()
    if kb.getKey("e"): drone.takeoff()

    if kb.getKey("z"):
        save_and_generate_description(img)
        time.sleep(0.3)

    return lr, fb, ud, yv


while True:
    lr, fb, ud, yv = get_keyboard_input()
    drone.send_rc_control(lr, fb, ud, yv)

    temp_img = drone.get_frame_read().frame
    img = cv2.resize(temp_img, (720, 480))
    cv2.imshow('frame', img)
    if cv2.waitKey(1) == 27:
        break

drone.streamoff()
cv2.destroyAllWindows()
