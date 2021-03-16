import RPi.GPIO as GPIO
import time
from Arm import Arm
from AdafruitIMU import AdafruitIMU
from time import sleep
import sys

sys.path.insert(1, 'beachbots2020\Code\support')

import Constants

class Chassis:

    def __init__(self, RPWMF, RPWMB, LPWMF, LPWMB, STEP, DIR, SWITCH, GRIPPER, ELBOW, BUCKET, MAX_BUCKET_CAPACITY):
        self.RPWMF = RPWMF
        self.RPWMB = RPWMB
        self.LPWMF = LPWMF
        self.LPWMB = LPWMB

        self.IMU = AdafruitIMU()
        self.arm = Arm(STEP, DIR, SWITCH, GRIPPER, ELBOW, BUCKET)
        self.MAX_BUCKET_CAPACITY = MAX_BUCKET_CAPACITY

        GPIO.setwarnings(False)  # disable warnings
        GPIO.setmode(GPIO.BOARD)  # set pin numbering system

        GPIO.setup(self.RPWMF, GPIO.OUT)
        GPIO.setup(self.RPWMB, GPIO.OUT)
        GPIO.setup(self.LPWMF, GPIO.OUT)
        GPIO.setup(self.LPWMB, GPIO.OUT)

        self.pi_rpwmf = GPIO.PWM(self.RPWMF, 1000)  # create PWM instance with frequency
        self.pi_rpwmb = GPIO.PWM(self.RPWMB, 1000)  # create PWM instance with frequency
        self.pi_lpwmf = GPIO.PWM(self.LPWMF, 1000)  # create PWM instance with frequency
        self.pi_lpwmb = GPIO.PWM(self.LPWMB, 1000)  # create PWM instance with frequency

        self.pi_rpwmf.start(0)  # start PWM of required Duty Cycle
        self.pi_rpwmb.start(0)  # start PWM of required Duty Cycle
        self.pi_lpwmf.start(0)  # start PWM of required Duty Cycle
        self.pi_lpwmb.start(0)  # start PWM of required Duty Cycle

    def get_max_bucket_capacity(self):
        return self.MAX_BUCKET_CAPACITY

    def reset_heading(self):
        self.IMU = AdafruitIMU()

    def drive(self, rightSpeed, leftSpeed):

        # for right side of drivetrain
        if (rightSpeed > 0) and (leftSpeed > 0):  # for going forward
            self.pi_rpwmf.ChangeDutyCycle(rightSpeed)  # drive right side forward
            self.pi_lpwmf.ChangeDutyCycle(leftSpeed)
            self.pi_rpwmb.ChangeDutyCycle(0)
            self.pi_lpwmb.ChangeDutyCycle(0)
        elif (rightSpeed < 0) and (leftSpeed < 0):  # for going backward
            self.pi_rpwmb.ChangeDutyCycle(abs(rightSpeed))
            self.pi_lpwmb.ChangeDutyCycle(abs(leftSpeed))
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_lpwmf.ChangeDutyCycle(0)
        elif (rightSpeed > 0) and (leftSpeed < 0):  # for point turn left
            self.pi_rpwmf.ChangeDutyCycle(rightSpeed)
            self.pi_lpwmb.ChangeDutyCycle(abs(leftSpeed))
            self.pi_rpwmb.ChangeDutyCycle(0)
            self.pi_lpwmf.ChangeDutyCycle(0)
        elif (rightSpeed < 0) and (leftSpeed > 0):  # for point turn right
            self.pi_rpwmb.ChangeDutyCycle(abs(rightSpeed))
            self.pi_lpwmf.ChangeDutyCycle(leftSpeed)
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_lpwmb.ChangeDutyCycle(0)
        elif (rightSpeed == 0) and (leftSpeed > 0):  # for swing turn right
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_rpwmb.ChangeDutyCycle(0)
            self.pi_lpwmf.ChangeDutyCycle(leftSpeed)
            self.pi_lpwmb.ChangeDutyCycle(0)
        elif (rightSpeed == 0) and (leftSpeed < 0):  # for swing turn right
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_rpwmb.ChangeDutyCycle(0)
            self.pi_lpwmb.ChangeDutyCycle(abs(leftSpeed))
            self.pi_lpwmf.ChangeDutyCycle(0)
        elif (rightSpeed > 0) and (leftSpeed == 0):  # for swing turn left
            self.pi_rpwmf.ChangeDutyCycle(rightSpeed)
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_lpwmf.ChangeDutyCycle(0)
            self.pi_lpwmb.ChangeDutyCycle(0)
        elif (rightSpeed < 0) and (leftSpeed == 0):  # for swing turn left
            self.pi_rpwmb.ChangeDutyCycle(abs(rightSpeed))
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_lpwmf.ChangeDutyCycle(0)
            self.pi_lpwmb.ChangeDutyCycle(0)
        elif rightSpeed == 0 and leftSpeed == 0:  # making robot stop
            self.pi_lpwmf.ChangeDutyCycle(0)
            self.pi_lpwmb.ChangeDutyCycle(0)
            self.pi_rpwmf.ChangeDutyCycle(0)
            self.pi_rpwmb.ChangeDutyCycle(0)

    def limit(self, val, minVal, maxVal):
        return min(max(val, minVal), maxVal)

    def point_turn_IMU(self, wantedAngle, speed):
        # relativePointAngle = wantedAngle - self.IMU.get_yaw()   # self.IMU.angleWrap(wantedAngle - currentAngle)

        while (self.IMU.get_yaw() > wantedAngle + Constants.DEG_THRESHOLD or self.IMU.get_yaw()
               < wantedAngle - Constants.DEG_THRESHOLD):
            # turn_speed = max(turn_speed, 50.0)
            # print("error", abs(wantedAngle-currentAngle))

            if wantedAngle > 0:
                self.drive(-speed, speed) # Turn right
            elif wantedAngle < 0:
                self.drive(speed, -speed) # Turn left
            elif self.IMU.get_yaw() > 0 and wantedAngle == 0:
                self.drive(speed, -speed) # Turn left
            elif self.IMU.get_yaw() < 0 and wantedAngle == 0:
                self.drive(-speed, speed) # Turn right

            #print("desired angle: ", wantedAngle)
            #print("current angle: ", self.IMU.get_yaw())

        self.drive(0, 0)


    def point_turn_basebot(self, wantedAngle, speed):
        # relativePointAngle = wantedAngle - self.IMU.get_yaw()   # self.IMU.angleWrap(wantedAngle - currentAngle)
        current_angle = self.IMU.get_yaw()

        if(current_angle > wantedAngle + Constants.DEG_THRESHOLD or current_angle < wantedAngle - Constants.DEG_THRESHOLD):
            # turn_speed = max(turn_speed, 50.0)
            # print("error", abs(wantedAngle-currentAngle))

            if wantedAngle > 0:
                self.drive(-speed, speed) # Turn right
            elif wantedAngle < 0:
                self.drive(speed, -speed) # Turn left
            elif self.IMU.get_yaw() > 0 and wantedAngle == 0:
                self.drive(speed, -speed) # Turn left
            elif self.IMU.get_yaw() < 0 and wantedAngle == 0:
                self.drive(-speed, speed) # Turn right
        else:
            self.drive(0,0)
            return True

        return False

    def swing_turn_IMU(self, currentAngle, wantedAngle, decelerationAngle, speed):
        relativePointAngle = wantedAngle - currentAngle  # self.IMU.angleWrap(wantedAngle - currentAngle)
        turn_speed = (relativePointAngle / decelerationAngle) * speed
        turn_speed = self.limit(turn_speed, -speed, speed)
        turn_speed = max(turn_speed, 50.0)
        if relativePointAngle > 0:
            self.drive(0, turn_speed)
        else:
            self.drive(turn_speed, 0)

    # duration in millis
    def driveStraightIMU(self, straightSpeed, curr_angle):
        # destination = self.current_milli_time() + duration  # calculate time when destination is reached
        target = curr_angle

        # while self.current_milli_time() < destination:  # while destination has not been reached

        # if(self.IMU.angleWrap(sensor.euler[0]) != None):
        #    absolute = self.IMU.angleWrap(sensor.euler[0])#getGyro() #continue reading gyro
        # else:
        #    absolute = 0
        absolute = self.IMU.get_yaw()
        leftSpeed = straightSpeed - (absolute - target)  # adjust motor speeds
        rightSpeed = straightSpeed + (absolute - target)
        # print("LEFTSPEED: ", leftSpeed)
        # print("RIGHTSPEED: ", rightSpeed)
        # print(rightSpeed, leftSpeed, absolute)
        #print("desired angle: ", curr_angle)
        #print("current angle: ", self.IMU.euler_from_quaternion())
        self.drive(rightSpeed, leftSpeed)  # write to chassis