# https://github.com/iRobotEducation/irobot-edu-python-sdk

# run "pip3 install irobot_edu_sdk"
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
from XWrite import writer
import time

print("Starting Irobot")
ROBOT = Create3(Bluetooth())

BASE_IR_SENSOR = 0
BASE_ANGLE = 0

INIT_SPEED = 5
SPEED = 10

INIT_BUMP = False

SAVE_DATA = True

DATA_WRITE = None
if SAVE_DATA:
    DATA_WRITE = writer()

def angle_difference(frst, scnd):
    value = frst - scnd
    if value > 180:
        return value - 360
    elif value < -180:
        return value + 360
    else:
        return value

def write_to_xls(sensors, angle):
    global DATA_WRITE
    DATA_WRITE.add_wall(sensors)
    DATA_WRITE.add_angle(angle)
    DATA_WRITE.go_next()
    DATA_WRITE.save()
    JUST_BUMP = False


# intitalizes the robot to look perpendicular to the wall
async def initiate_robot():
    global INIT_BUMP, BASE_IR_SENSOR, INIT_SPEED, BASE_ANGLE
    while not INIT_BUMP:
        await ROBOT.move(10)

    sensors = (await ROBOT.get_ir_proximity()).sensors
    topValue = sensors[3]
    await ROBOT.turn_left(1)
    sensors = (await ROBOT.get_ir_proximity()).sensors
    if sensors[3] > topValue:
        while sensors[3] > topValue:
            topValue = sensors[3]
            await ROBOT.turn_left(1)
            sensors = (await ROBOT.get_ir_proximity()).sensors
        await ROBOT.turn_right(1)
    else:
        await ROBOT.turn_right(2)
        sensors = (await ROBOT.get_ir_proximity()).sensors
        while sensors[3] > topValue:
            topValue = sensors[3]
            await ROBOT.turn_right(1)
            sensors = (await ROBOT.get_ir_proximity()).sensors
        await ROBOT.turn_left(1)
    
    BASE_IR_SENSOR = sensors[3]
    BASE_ANGLE = (await ROBOT.get_position()).heading

@event(ROBOT.when_play)
async def play(ROBOT):
    global BASE_IR_SENSOR, SPEED, CORRECTING, DIRECTION, JUST_BUMP, SAVE_DATA, GOING_FORWARD, INIT_BUMP
    door_counter = 0
    prev_prob = 0
    await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    print('start walk')
    while True:
        INIT_BUMP = False
        await initiate_robot()
        sensors = (await ROBOT.get_ir_proximity()).sensors
        BASE_IR_SENSOR = sensors[3]
        
        # adding the sensor values to the network
        angleDiff = angle_difference((await ROBOT.get_position()).heading, BASE_ANGLE)
        if SAVE_DATA:
            write_to_xls(sensors[3], angleDiff)
        print(BASE_IR_SENSOR)
        await ROBOT.turn_left(90)

        # moving forward
        await ROBOT.move(20)
        await ROBOT.turn_right(90)
        

# checks if the robot bumped. readjusts the robot if needed
@event(ROBOT.when_bumped, [True, True])
async def bump(robot):
    global INIT_BUMP, ROBOT
    await ROBOT.stop()
    print('bump')
    await ROBOT.move(-5)
    INIT_BUMP = True



ROBOT.play()
