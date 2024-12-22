from tello import Tello
import time
import utils

class TelloMovement:
    def __init__(self, tello: Tello):
        self.tello = tello
        self.tts_engine = utils.init_tts_engine(voice_name= "com.apple.speech.synthesis.voice.samantha")

    def move_to_position(self, x: int, y: int, z: int, speed: int):
        self.tello.go_xyz_speed(x, y, z, speed)
        message = f"I am moving."
        utils.speak(self.tts_engine, message)
    
    def takeoff(self):
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
