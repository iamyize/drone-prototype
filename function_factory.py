import base64
import os
import time

from tello import Tello
import datetime
import utils
from ultralytics import YOLO

import openai
import cv2
import pathlib as Path


class TelloMovement:
    def __init__(self, tello: Tello):
        api_key = utils.load_file('api_key.txt')
        self.tello = tello
        self.tts_engine = utils.init_tts_engine()
        self.client = openai.OpenAI(api_key=api_key)

    def connect(self):
        self.tello.connect()
        message = f"Connected. Battery at {self.tello.get_battery()}%."
        print(message)
        utils.speak(self.tts_engine, message)

    def sleep(self):
        time.sleep(4)

    def move_to_position(self, x: int, y: int, z: int, speed: int):
        self.tello.go_xyz_speed(x, y, z, speed)
        message = f"I am moving."
        utils.speak(self.tts_engine, message)

    def origin_to_table(self):
        self.tello.go_xyz_speed(50, 0, 0, 25)
        message = f"I am moving to the window."
        utils.speak(self.tts_engine, message)

    def table_to_origin(self):
        self.tello.go_xyz_speed(-50, 0, 0, 25)
        message = f"I am moving back."
        utils.speak(self.tts_engine, message)
    
    def table_to_shelf(self):
        self.tello.go_xyz_speed(0, 0, 30, 25)
        self.tello.go_xyz_speed(50, 0, 0, 25)
        message = f"I am moving to the shelf."
        utils.speak(self.tts_engine, message)

    def search_the_room(self):
        self.tello.go_xyz_speed(0, 0, 0, 25)
        message = f"I am scanning the room."
        utils.speak(self.tts_engine, message)

    def take_off(self):
        self.tello.takeoff()
        message = f"I am taking off."
        utils.speak(self.tts_engine, message)

    def land(self):
        self.tello.land()
        message = f"I am landing."
        utils.speak(self.tts_engine, message)

    def get_status(self):
        battery = self.tello.get_battery()
        # flight_time = self.tello.query_flight_time()
        # temperature = self.tello.query_temperature()

        message = (
            f"Here's my current status: "
            f"Battery is at {battery} percent, "
            # f"I've been flying for {flight_time} seconds, "
            # f"and the temperature is {temperature} degrees celsius."
        )
        utils.speak(self.tts_engine, message)

    def capture_image(self):
        self.tello.streamon()
        current_time = time.time()

        # Min 5 seconds to escape black screen input
        while time.time() < current_time + 5:
            temp_img = self.tello.get_frame_read().frame

        self.tello.streamoff()

        elapsed_time = time.time() - current_time
        # image_path = f"resources/images/image1.jpg"
        image_path = f"resources/images/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        print(f"img capture time: {elapsed_time}")

        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        cv2.imwrite(image_path, temp_img)

        return image_path

    def object_detection(self):

        image_path = self.capture_image()
        # self.tello.send_keepalive()
        time.sleep(2)

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        prompt = "List the 3 most important objects in the image. Keep it brief."
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
        utils.speak(self.tts_engine, message)
        print(message)

    def text_recognition(self):

        image_path = self.capture_image()
        time.sleep(2)

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        prompt = "Read the text in the image."
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
        utils.speak(self.tts_engine, message)
        print(message)

    def object_yolo(self, image_path):
        model = YOLO("yolo11n.pt") # yolo11
        current_time = time.time()
        result = model(image_path)
        elapsed_time = time.time() - current_time
        print(f"detection time: {elapsed_time}")
        print(result)
        message = f"I have detected {result} in the image."
        utils.speak(self.tts_engine, message)


    # def chatgpt_read_image(self):
    #     self.tello.streamon()
    #     temp_img = self.tello.get_frame_read().frame
    #
    #     image_path = f"resources/images/{datetime.datetime().now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    #
    #     os.makedirs(os.path.dirname(image_path), exist_ok=True)
    #
    #     cv2.imwrite(image_path, temp_img)
    #
    #     with open(image_path, "rb") as image_file:
    #         base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    #
    #     prompt = "Identify and describe all objects in the image"
    #     image_description = self.client.chat.completions.create(
    #         model="gpt-4o",
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {"type": "text", "text": prompt},
    #                     {
    #                         "type": "image_url",
    #                         "image_url": {
    #                             "url": f"data:image/jpeg;base64,{base64_image}"
    #                         },
    #                     },
    #                 ],
    #             }
    #         ],
    #         max_tokens=50,
    #     )
    #
    #     message = image_description.choices[0].message.content
    #     utils.speak(self.tts_engine, message)
    #     self.tello.streamoff()

