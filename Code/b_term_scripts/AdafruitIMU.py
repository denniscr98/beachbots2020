import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055


class AdafruitIMU:

    def __init__(self):
        i2c = I2C(1)  # Device is /dev/i2c-1
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)

    def angleWrap(self, angle):
        angle %= 360
        while angle > 180:
            angle -= 360
        while angle <= -180:
            angle += 360
        return angle

    def getAngle(self):
        angle = self.sensor.euler[0]
        return angle