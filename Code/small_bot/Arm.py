import RPi.GPIO as GPIO
import time
from time import sleep
from ServoController import ServoController
import sys

sys.path.insert(1, 'beachbots2020\Code\support')

import Constants

class Arm:

    def __init__(self, STEP, DIR, SWITCH, GRIPPER, ELBOW, BUCKET):
        self.STEP = STEP
        self.DIR = DIR
        self.SWITCH = SWITCH
        self.servo = ServoController(GRIPPER, ELBOW, BUCKET)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.STEP, GPIO.OUT)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.SWITCH, GPIO.IN)  # , pull_up_down=GPIO.PUD_UP)
        self.usleep = lambda x: time.sleep(x / 1000000.0)
        self.shoulder_current = 0.0

        self.calibrate()

    def move_shoulder_angle(self, angle):
        target = angle - self.shoulder_current
        steps = abs(int(target // Constants.STEP_ANGLE))
        num_steps = 0
        '''
        print("target:",  target)
        print("steps: ", steps)
        print("current angle: ", self.shoulder_current)
        '''
        if target < 0:
            GPIO.output(self.DIR, GPIO.LOW)
        else:
            GPIO.output(self.DIR, GPIO.HIGH)
        while num_steps < steps:
            GPIO.output(self.STEP, GPIO.HIGH)
            self.usleep(500)
            GPIO.output(self.STEP, GPIO.LOW)
            self.usleep(500)
            num_steps += 1
        self.shoulder_current += target
        '''
        print("target:",  target)
        print("steps: ", steps)
        print("current angle: ", self.shoulder_current)
        '''

    def calibrate(self):
        self.servo.bucket(False)
        self.servo.elbow(Constants.UP_POSE_ELBOW)  # UP position for elbow
        self.servo.gripper(False)  # Closed position for gripper
        GPIO.output(self.DIR, GPIO.LOW)
        while not GPIO.input(self.SWITCH):
            GPIO.output(self.STEP, GPIO.HIGH)
            self.usleep(500)
            GPIO.output(self.STEP, GPIO.LOW)
            self.usleep(500)
        self.shoulder_current = 0
        # print("current angle: ", self.shoulder_current)
        self.move_shoulder_angle(30)

    # def switch_press(self):
    #    pressed = GPIO.input(self.SWITCH)
    #    return pressed
    # print(GPIO.input(self.SWITCH))

    def pickup(self):
        # self.servo.gripper(True)

        self.move_shoulder_angle(100)  # original 30 changed for camera

        sleep(2)

        self.servo.gripper(True)
        sleep(4)
        self.servo.elbow(Constants.DOWN_POSE_ELBOW)
        sleep(3)
        self.move_shoulder_angle(45)
        self.servo.gripper(False)
        sleep(3)
        self.servo.elbow(Constants.UP_POSE_ELBOW)
        self.move_shoulder_angle(115)
        sleep(2)
        self.servo.gripper(True)
        sleep(3)
        self.move_shoulder_angle(30)
        self.servo.gripper(False)
