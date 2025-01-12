import base64
import os
import time

from tello import Tello
import datetime
import utils
from ultralytics import YOLO

import openai
import cv2


class TelloMovement:
    def __init__(self, tello: Tello):
        api_key = utils.load_file('api_key.txt')
        self.tello = tello
        self.tts_engine = utils.init_tts_engine()
        self.client = openai.OpenAI(api_key=api_key)
        self.locations = ["window", "table", "floor"]

    def connect(self):
        self.tello.connect()
        message = f"Connected. Battery at {self.tello.get_battery()}%."
        print(message)
        utils.speak(self.tts_engine, message)

    def move_to_position(self, x: int, y: int, z: int, speed: int):
        message = f"I am moving."
        utils.speak(self.tts_engine, message)
        self.tello.go_xyz_speed(x, y, z, speed)

    def move_to_window(self):
        message = f"I am moving to the window."
        utils.speak(self.tts_engine, message)
        self.tello.go_xyz_speed(50, 0, 0, 25)

    def move_to_table(self):
        self.tello.rotate_counter_clockwise(90)
        # self.tello.go_xyz_speed()

    def move_to_floor(self):
        self.tello.rotate_counter_clockwise(90)
        self.tello.go_xyz_speed(50, 0, 0, 25)

    def return_to_origin(self):
        message = f"I am moving back."
        utils.speak(self.tts_engine, message)
        self.tello.go_xyz_speed(-50, 0, 0, 25)

    def take_off(self):
        message = f"I am taking off."
        utils.speak(self.tts_engine, message)
        self.tello.takeoff()

    def land(self):
        message = f"I am landing."
        utils.speak(self.tts_engine, message)
        self.tello.land()

    # query_xxx gives different formats which cannot just be cast to int, e.g. time->0s, temp->80-82C
    # safer to just use get_xxx unless want to parse through each possible format
    def get_status(self):
        battery = self.tello.get_battery()
        flight_time = self.tello.get_flight_time()
        temperature = self.tello.get_temperature()

        message = (
            f"Here's my current status: "
            f"Battery is at {battery} percent, "
            f"I've been flying for {flight_time} seconds, "
            f"and the temperature is {temperature} degrees celsius."
        )
        utils.speak(self.tts_engine, message)

    def capture_image(self):
        print("capturing image")
        self.tello.streamon()
        current_time = time.time()

        temp_img_obj = self.tello.get_frame_read()
        # This removes the black screen initial input
        time.sleep(1)

        self.tello.streamoff()

        temp_img = temp_img_obj.frame

        elapsed_time = time.time() - current_time
        image_path = f"resources/images/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        print(f"img capture time: {elapsed_time}")

        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(image_path, temp_img)

        return image_path

    def object_detection(self):
        message = f"I am detecting objects"
        utils.speak(self.tts_engine, message)

        image_path = self.capture_image()
        print("Detecting objects")
        self.tello.send_keepalive()

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        prompt = "Identify and list the 3 most important objects in the image. Keep it brief."
        image_description = self.client.chat.completions.create(
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
            max_tokens=50,
        )

        message = image_description.choices[0].message.content
        self.tello.send_keepalive()
        print(message)
        utils.speak(self.tts_engine, message)

    def check_item(self, item, image_paths):
        message = f"I am looking for {item}"
        utils.speak(self.tts_engine, message)

        print(f"Checking for {item}")
        current_time = time.time()

        base64_images = []
        for image_path in image_paths:
            with open(image_path, "rb") as image_file:
                base64_images.append(base64.b64encode(image_file.read()).decode('utf-8'))

        prompt = (f"Which image contains the {item}? Give only the image number."
                  f"If none of the images contain the {item}, give 0."
                  f"Do not generate any other text.")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        for base64_image in base64_images:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        image_description = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300,
        )

        message = image_description.choices[0].message.content
        if int(message) == 0:
            message = f"The {item} cannot be found."
        else:
            message = f"The {item} is at the {self.locations[int(message) - 1]}."
        print(message)
        elapsed_time = time.time() - current_time
        print(elapsed_time)
        utils.speak(self.tts_engine, message)

    def find_item(self, item):
        image_paths = []
        self.take_off()
        self.move_to_window()
        image_paths.append(self.capture_image())
        self.move_to_table()
        image_paths.append(self.capture_image())
        self.move_to_floor()
        image_paths.append(self.capture_image())
        self.land()
        self.check_item(item, image_paths)

    def check_object_yolo(self, image_path):
        model = YOLO("yolo11n.pt") # yolo11
        current_time = time.time()
        result = model(image_path)
        elapsed_time = time.time() - current_time
        print(f"detection time: {elapsed_time}")
        message = f"I have detected {result} in the image."
        utils.speak(self.tts_engine, message)

