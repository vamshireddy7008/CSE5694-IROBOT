# https://github.com/iRobotEducation/irobot-edu-python-sdk

# run "pip3 install irobot_edu_sdk"
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
from irobot_BN2 import IrobotNetwork as IRN
from XWrite import writer
import time

print("Starting Irobot")
ROBOT = Create3(Bluetooth())
NETWORK = IRN()

BASE_IR_SENSOR = 0
BASE_ANGLE = 0

INIT_SPEED = 5
SPEED = 10

INIT_BUMP = False

CORRECTING = False

DIRECTION = 'T' # S == Stright, T == Turn

GOING_FORWARD = True

QUARTER_NOTE_LENGTH = 0.5

SAVE_DATA = True

DATA_WRITE = None
if SAVE_DATA:
    DATA_WRITE = writer()

# plays zelda chest music then goes to the next task
async def go_to_next_task():
    global ROBOT, GOING_FORWARD, QUARTER_NOTE_LENGTH
    GOING_FORWARD = False
    eighth_note = 0.5 * QUARTER_NOTE_LENGTH
    await ROBOT.play_note(Note.C6, eighth_note)
    await ROBOT.play_note(Note.A5_SHARP, eighth_note)
    await ROBOT.play_note(Note.B5, eighth_note)
    await ROBOT.play_note(Note.C4, QUARTER_NOTE_LENGTH)
    await ROBOT.turn_right(180)
    await ROBOT.move(0)

# plays mario level completion music
async def play_complete():
    global QUARTER_NOTE_LENGTH, ROBOT
    eighth_note = 0.5 * QUARTER_NOTE_LENGTH
    quat_triplet = QUARTER_NOTE_LENGTH / 3
    await ROBOT.play_note(Note.C6, quat_triplet)
    await ROBOT.play_note(Note.D6, quat_triplet)
    await ROBOT.play_note(Note.F6, quat_triplet)
    await ROBOT.play_note(Note.C5, quat_triplet)
    await ROBOT.play_note(Note.E5, quat_triplet)
    await ROBOT.play_note(Note.G4, QUARTER_NOTE_LENGTH)
    await ROBOT.play_note(Note.E4, eighth_note)
    time.sleep(eighth_note)
    time.sleep(quat_triplet)
    await ROBOT.play_note(Note.C6, quat_triplet)
    await ROBOT.play_note(Note.D6_SHARP, quat_triplet)
    await ROBOT.play_note(Note.F6_SHARP, quat_triplet)
    await ROBOT.play_note(Note.C5, quat_triplet)
    await ROBOT.play_note(Note.D5_SHARP, quat_triplet)
    await ROBOT.play_note(Note.G4_SHARP, QUARTER_NOTE_LENGTH)
    await ROBOT.play_note(Note.E4, eighth_note)
    time.sleep(eighth_note)
    time.sleep(quat_triplet)
    await ROBOT.play_note(Note.D6, quat_triplet)
    await ROBOT.play_note(Note.E6, quat_triplet)
    await ROBOT.play_note(Note.A5_SHARP, quat_triplet)
    await ROBOT.play_note(Note.D5, quat_triplet)
    await ROBOT.play_note(Note.F5, quat_triplet)
    await ROBOT.play_note(Note.A4_SHARP, QUARTER_NOTE_LENGTH)
    await ROBOT.play_note(Note.A4_SHARP, eighth_note)
    await ROBOT.play_note(Note.A4_SHARP, eighth_note)
    await ROBOT.play_note(Note.A4_SHARP, eighth_note)
    await ROBOT.play_note(Note.C4, 4 * QUARTER_NOTE_LENGTH)

def angle_difference(frst, scnd):
    value = frst - scnd
    if value > 180:
        return value - 360
    elif value < -180:
        return value + 360
    else:
        return value

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

# fixes the robot direction
async def fix_robot_direction():    
    global INIT_BUMP
    INIT_BUMP = True
    initiate_robot()
g
@event(ROBOT.when_play)
async def play(ROBOT):
    global BASE_IR_SENSOR, SPEED, CORRECTING, DIRECTION
    door_counter = 0
    prev_prob = 0
    await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    await initiate_robot()
    await ROBOT.turn_left(90)
    DIRECTION = 'S'
    #await ROBOT.reset_navigation()
    sensors = (await ROBOT.get_ir_proximity()).sensors
    #print(sensors)
    print('start walk')

    await ROBOT.set_wheel_speeds(SPEED,SPEED)
    while True:
        if CORRECTING:
            time.sleep(1)
            continue

        # moving forward
        await ROBOT.move(20)
        
        if CORRECTING:
            continue

        # turning towards the wall
        if GOING_FORWARD:
            await ROBOT.turn_right(90)
        else:
            await ROBOT.turn_left(90)
        DIRECTION = 'T'

        if CORRECTING:
            continue

        # SENSORS are listed from left to right [L, ., ., ., ., ., R]
        # the stronger the sensor value. the close the object is
        sensors = (await ROBOT.get_ir_proximity()).sensors

        # adding the sensor values to the network
        NETWORK.add_scanner_value(sensors[3])
        NETWORK.add_bumper_value(0)
        angleDiff = angle_difference((await ROBOT.get_position()).heading, BASE_ANGLE)
        NETWORK.add_wheel_value(angleDiff)

        # calculating the probability
        prob = NETWORK.calculate_probability()
        print ("probability: " + str(prob))

        # check if we need to readjust the robot
        wallprob = NETWORK.calculate_probability(type ='wall', time=1)
        if wallprob > 0.6 and ( -40 <BASE_IR_SENSOR - sensors[3] > 40 ):
            fix_robot_direction()

        # check if we passed a door
        if prob < 0.5 and prev_prob > 0.5:
            door_counter += 1
            await ROBOT.play_note(Note.A5, 0.20)
            print("door counter: " + str(door_counter))

        # check if we passed 3 doors
        if door_counter == 3:
            if GOING_FORWARD: # turn around
                GOING_FORWARD = False
                await ROBOT.turn_left(90)
                await ROBOT.move(40)
                await go_to_next_task()
                door_counter = 0
                prev_prob = 0
                DIRECTION = 'S'
                continue
            else: # completing the task
                await ROBOT.turn_right(90)
                await ROBOT.move(40)
                await ROBOT.stop()
                await play_complete()
                break
        
        # turning parallel to the wall
        if GOING_FORWARD:
            await ROBOT.turn_left(90)
        else:
            await ROBOT.turn_right(90)
        prev_prob = prob
        DIRECTION = 'S'

# checks if the robot bumped. readjusts the robot if needed
@event(ROBOT.when_bumped, [True, True])
async def bump(robot):
    global INIT_BUMP, DIRECTION, CORRECTING, GOING_FORWARD
    await ROBOT.stop()
    print('bump')
    await ROBOT.move(-5)
    if not INIT_BUMP:
        INIT_BUMP = True
    else:
        CORRECTING = True
        NETWORK.add_bumper_value(1)

        if DIRECTION == 'S':
            if GOING_FORWARD:
                await ROBOT.turn_right(90)
            else:
                await ROBOT.turn_left(90)
        initiate_robot()
        await ROBOT.move(-10)
        await ROBOT.turn_left(90)
        CORRECTING = False



ROBOT.play()
