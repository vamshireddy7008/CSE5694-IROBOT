# https://github.com/iRobotEducation/irobot-edu-python-sdk

# run "pip3 install irobot_edu_sdk"
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
from irobot_BN import IrobotNetwork as IRN
import time

print("Starting Irobot")
ROBOT = Create3(Bluetooth())
NETWORK = IRN()

BASE_IR_SENSOR = 0
BASE_ANGLE = 0

INIT_SPEED = 5
SPEED = 10

INIT_BUMP = False

def angle_difference(frst, scnd):
    value = frst - scnd
    if value > 180:
        return value - 360
    elif value < -180:
        return value + 360
    else:
        return value


async def initiate_robot():
    global INIT_BUMP, BASE_IR_SENSOR, INIT_SPEED
    await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    while not INIT_BUMP:
        await ROBOT.move(5)

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
    #print("BASE_SENSOR: " + str(BASE_IR_SENSOR))
    BASE_ANGLE = (await ROBOT.get_position()).heading
    await ROBOT.turn_left(90)

'''
async def follow_wall():
    sensors = (await ROBOT.get_ir_proximity()).sensors
    if sensors[-1] > 5 or sensors[-1] <= 0:
        await ROBOT.move(-2)
    while sensors[-1] > 5 or sensors[-1] <= 0:
        #print("adjusting")
        if sensors[-1] > 5:
            await ROBOT.turn_left(2)
        else:
            await ROBOT.turn_right(2)
        sensors = (await ROBOT.get_ir_proximity()).sensors
'''

@event(ROBOT.when_play)
async def play(ROBOT):
    global BASE_IR_SENSOR, SPEED
    await initiate_robot()
    #await ROBOT.reset_navigation()
    sensors = (await ROBOT.get_ir_proximity()).sensors
    #print(sensors)
    print('start walk')

    await ROBOT.set_wheel_speeds(SPEED,SPEED)
    while True:
        await ROBOT.move(20)
        await ROBOT.turn_right(90)
        #print (await ROBOT.get_position())
        time.sleep(1)

        # SENSORS are listed from left to right [L, ., ., ., ., ., R]
        # the stronger the sensor value. the close the object is
        sensors = (await ROBOT.get_ir_proximity()).sensors
        #print(sensors)
        NETWORK.add_scanner_value(sensors[3] - BASE_IR_SENSOR)
        NETWORK.add_bumper_value(0)
        angleDiff = angle_difference((await ROBOT.get_position()).heading, BASE_ANGLE)
        NETWORK.add_wheel_value(angleDiff)
        await ROBOT.turn_left(90)
        print ("probability: " + str(NETWORK.calculate_probability()))

@event(ROBOT.when_bumped, [True, True])
async def talk(robot):
    global INIT_BUMP
    await ROBOT.stop()
    print('bump')
    await ROBOT.move(-5)
    if not INIT_BUMP:
        INIT_BUMP = True
    else:
        NETWORK.add_bumper_value(1)



ROBOT.play()
