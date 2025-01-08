import sys

import tello
import voice_input
import code_generation
import utils
from function_factory import TelloMovement
from ultralytics import YOLO


if __name__ == '__main__':
    item = "bag"
    drone = TelloMovement(tello.Tello())
    # drone.connect()
    drone.check_item(item, ["resources/images/2025-01-09_00-22-15.jpg","resources/images/2025-01-09_00-22-21.jpg","resources/images/2025-01-09_00-22-29.jpg"])
