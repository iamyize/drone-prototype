import base64

from tello import Tello
import datetime
import utils
import openai
import cv2
import pathlib as Path


class TelloMovement:
    def __init__(self, tello: Tello):
        self.tello = tello
        self.tts_engine = utils.init_tts_engine()
        self.client = openai.OpenAI(api_key=api_key)

    def connect(self):
        self.tello.connect()
        message = f"Connected. Battery at {self.tello.get_battery()}%."
        print(message)
        utils.speak(self.tts_engine, message)

    def move_to_position(self, x: int, y: int, z: int, speed: int):
        self.tello.go_xyz_speed(x, y, z, speed)
        message = f"I am moving."
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
        battery = self.tello.query_battery()
        flight_time = self.tello.query_flight_time()
        temperature = self.tello.query_temperature()

        message = (
            f"Here's my current status: "
            f"Battery is at {battery} percent, "
            f"I've been flying for {flight_time} seconds, "
            f"and the temperature is {temperature} degrees celsius."
        )
        utils.speak(self.tts_engine, message)

    def chatgpt_read_image(self):
        self.tello.streamon()
        temp_img = self.tello.get_frame_read().frame

        Path("resources/images").mkdir(parents=True, exist_ok=True)

        image_path = f"resources/images/{datetime.datetime().now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"

        cv2.imwrite(image_path, temp_img)

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        prompt = "Identify and describe all objects in the image"
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
        self.tello.streamoff()

