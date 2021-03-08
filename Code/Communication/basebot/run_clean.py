from Chassis import Chassis
import socket
from time import sleep

RPWMF = 22  # PWM
RPWMB = 29

LPWMF = 31  # PWM
LPWMB = 36

DIR = 38
STEP = 35
SWITCH = 13

GRIPPER = 1
ELBOW = 0
BUCKET = 2

DOWN_POSE_ELBOW = 5300
UP_POSE_ELBOW = 8000

chassis = Chassis(RPWMF, RPWMB, LPWMF, LPWMB, STEP, DIR, SWITCH, GRIPPER, ELBOW, BUCKET)
current_state = b'drive'
trash_detected = false
trash_count = 0
last_turn = ' '

TCP_IP = '192.168.4.2'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)

recieved = ""


counter = 0
finished_clean = false

while not finished_clean or trash_count < 4:

    if trash_count >= 4:
        current_state = b'stop'

    # Constantly updating current yaw angle
    euler_angles = chassis.IMU.euler_from_quaternion()

    data = conn.recv(BUFFER_SIZE)

    if data != b'middle':
        current_state = data

    if current_state == b'drive':
        chassis.driveStraightIMU(100, 100) #drive at full speed for 100ms

        if trash_detected:
            chassis.arm.pickup(0)
            sleep(2) #wait 2 secs
            chassis.arm.pickup(1)
            trash_count += trash_count
            trash_detected = false

        if april_tag_is_out_of_range:
            if last_turn != current_state:
                current_state = b'turnright'
            else:
                current_state = b'turnleft'

            last_turn = current_state

    if current_state == b'turnleft':
        chassis.swing_turn_IMU(chassis, euler_angles, -180, 5, 50)
        if abs(-10 - euler_angles) < 0.5:
            current_state = b'drive'

    elif current_state == b'turnright':
        chassis.swing_turn_IMU(chassis, euler_angles, 180, 5, 50)
        if abs(10 - euler_angles) < 0.5:
            current_state = b'drive'

    elif current_state == b'stop':
        chassis.drive(0, 0)
        break

    conn.send(data)  # echo

conn.close()