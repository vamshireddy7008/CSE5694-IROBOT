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

WALL_AVG = NETWORK.NetworkSet['Wall_Nodes']['scanner'].normal_dist.mean
WALL_STD_DEV = NETWORK.NetworkSet['Wall_Nodes']['scanner'].normal_dist.sd

DOOR_AVG = NETWORK.NetworkSet['Door_Nodes']['scanner'].normal_dist.mean
DOOR_STD_DEV = NETWORK.NetworkSet['Door_Nodes']['scanner'].normal_dist.sd

BASE_IR_SENSOR = 0
BASE_ANGLE = 0

INIT_SPEED = 4
SPEED = 15

RIGHT = 90
LEFT = 90


INIT_BUMP = False

JUST_BUMP = False

SINGLE_BUMP = False

CORRECTING = False

DIRECTION = 'T' # S == Stright, T == Turn

GOING_FORWARD = True

QUARTER_NOTE_LENGTH = 0.3

SAVE_DATA = True

PENDING_FIX = False

DATA_WRITE = None
if SAVE_DATA:
    DATA_WRITE = writer()

# plays zelda chest music then goes to the next task
async def go_to_next_task():
    global ROBOT, GOING_FORWARD, QUARTER_NOTE_LENGTH
    GOING_FORWARD = False
    eighth_note = 0.5 * QUARTER_NOTE_LENGTH
    await ROBOT.play_note(Note.C4, eighth_note)
    await ROBOT.play_note(Note.A5_SHARP, eighth_note)
    await ROBOT.play_note(Note.B5, eighth_note)
    await ROBOT.play_note(Note.C6, QUARTER_NOTE_LENGTH)
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

def write_to_xls(sensors, angle, prob_door, prob_wall, prob_frame):
    global NETWORK, JUST_BUMP, DATA_WRITE
    if prob_door > prob_wall and prob_door > prob_frame:
        DATA_WRITE.add_door(sensors)
    if prob_wall > prob_door and prob_wall > prob_frame:
        DATA_WRITE.add_wall(sensors)
    if prob_frame > prob_door and prob_frame > prob_wall:
        DATA_WRITE.add_frame(sensors)
    DATA_WRITE.add_angle(angle)
    if JUST_BUMP:
        DATA_WRITE.add_Bump()
    DATA_WRITE.go_next()
    DATA_WRITE.save()
    JUST_BUMP = False


# intitalizes the robot to look perpendicular to the wall
async def initiate_robot():
    global INIT_BUMP, BASE_IR_SENSOR, INIT_SPEED, BASE_ANGLE
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
        await ROBOT.turn_right(0.5)
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
async def reset_robot_direction():
    global INIT_BUMP, BASE_IR_SENSOR, ROBOT, INIT_SPEED, SPEED, WALL_AVG, WALL_STD_DEV
    await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    INIT_BUMP = False
    await initiate_robot()
    sensors = (await ROBOT.get_ir_proximity()).sensors
    await fix_robot_direction(WALL_AVG, WALL_STD_DEV)
    BASE_IR_SENSOR = sensors[3]
    print(BASE_IR_SENSOR)

async def fix_robot_direction(value, threshold):    
    global INIT_BUMP, BASE_IR_SENSOR, ROBOT
    prev = ''
    await initiate_robot()
    sensors = (await ROBOT.get_ir_proximity()).sensors
    while sensors[3] - value > threshold or sensors[3] - value < -1 * threshold:
        if sensors[3] > value:
            await ROBOT.move(-1)
            if prev == 'b':
                break
            prev = 'f'
        else:
            await ROBOT.move(1)
            if prev == 'f':
                break
            prev = 'b'
        sensors = (await ROBOT.get_ir_proximity()).sensors
    print(BASE_IR_SENSOR)

@event(ROBOT.when_play)
async def play(ROBOT):
    global BASE_IR_SENSOR, SPEED, CORRECTING, DIRECTION, JUST_BUMP, SAVE_DATA, GOING_FORWARD, PENDING_FIX, WALL_AVG, WALL_STD_DEV, DOOR_AVG, DOOR_STD_DEV, SINGLE_BUMP
    global RIGHT, LEFT
    door_counter = 0
    prev_prob = 0
    lastIsFrame = False
    lastIsDoor = False
    #await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    await initiate_robot()
    await fix_robot_direction(WALL_AVG, WALL_STD_DEV)
    await ROBOT.turn_right(1)
    sensors = (await ROBOT.get_ir_proximity()).sensors
    BASE_IR_SENSOR = sensors[3]
    print('starting sensor' + str(BASE_IR_SENSOR))
    await ROBOT.turn_left(LEFT)
    DIRECTION = 'S'
    print('start walk')

    await ROBOT.set_wheel_speeds(SPEED,SPEED)
    while True:
        SINGLE_BUMP = False
        if CORRECTING:
            print("correcting")
            if DIRECTION == 'S':
                if GOING_FORWARD:
                    await ROBOT.turn_right(RIGHT)
                else:
                    await ROBOT.turn_left(LEFT)
            await initiate_robot()
            await ROBOT.move(-5)
            if GOING_FORWARD:
                await ROBOT.turn_left(LEFT)
            else:
                await ROBOT.turn_right(RIGHT)
            CORRECTING = False

        # moving forward
        if PENDING_FIX:
            await ROBOT.move(40)
        elif lastIsDoor:
            await ROBOT.move(10)
        else:
            await ROBOT.move(15)
        
        if CORRECTING:
            continue

        # turning towards the wall
        if GOING_FORWARD:
            await ROBOT.turn_right(RIGHT)
        else:
            await ROBOT.turn_left(LEFT)
        DIRECTION = 'T'

        if CORRECTING:
            continue
        if PENDING_FIX:
            NETWORK.remove_bump()
            await reset_robot_direction()
            #await ROBOT.set_wheel_speeds(SPEED,SPEED)
            PENDING_FIX = False

        # SENSORS are listed from left to right [L, ., ., ., ., ., R]
        # the stronger the sensor value. the close the object is
        sensors = (await ROBOT.get_ir_proximity()).sensors
        
        # adding the sensor values to the network
        NETWORK.add_scanner_value(sensors[3])
        NETWORK.add_bumper_value(0)
        angleDiff = angle_difference((await ROBOT.get_position()).heading, BASE_ANGLE)
        NETWORK.add_wheel_value(angleDiff)
        print("sensor: " + str(sensors[3]))
        # calculating the probability
        prob = NETWORK.calculate_probability()
        print ("probability: " + str(100 * prob))

        # check if we need to readjust the robot
        doorprob = NETWORK.calculate_probability(type = 'door', time = 1)
        wallprob = NETWORK.calculate_probability(type = 'wall', time = 1)
        frameprob = NETWORK.calculate_probability(type = 'frame', time = 1)
        print("door: " + str(100 * doorprob))
        print("wall: " + str(100 * wallprob))
        print("frame: " + str(100 * frameprob))
        if wallprob > 0.5 and ( -1 * 20 > WALL_AVG - sensors[3] or WALL_AVG - sensors[3] > 20):
            await fix_robot_direction(WALL_AVG, WALL_STD_DEV/2)
            await ROBOT.turn_right(1)
            if WALL_AVG > sensors[3]:
                await ROBOT.turn_right(1)
            else:
                await ROBOT.turn_left(1)

        # await fix_robot_direction()
        if frameprob > 0.5:
            if lastIsFrame:
                await reset_robot_direction()
                #await ROBOT.set_wheel_speeds(SPEED,SPEED)
            lastIsFrame = True
        else:
            lastIsFrame = False

        # check if we passed a door
        if prob < 0.5 and prev_prob > 0.5:
            door_counter += 1
            PENDING_FIX = True
            NETWORK.remove_bump()
            await ROBOT.play_note(Note.A5, 0.20)
            print("door counter: " + str(door_counter))
        if doorprob > 0.5:
            if lastIsDoor and DOOR_AVG - sensors[3] > DOOR_STD_DEV or  DOOR_AVG - sensors[3] < -1 * DOOR_STD_DEV:
                await fix_robot_direction(DOOR_AVG, DOOR_STD_DEV * 1.3)
            lastIsDoor = True
        else:
            lastIsDoor = False
                
        if sensors[3] < 120:
            await reset_robot_direction()
        # check if we passed 3 doors
        if door_counter == 3:
            if GOING_FORWARD: # turn around
                GOING_FORWARD = False
                PENDING_FIX = False
                await ROBOT.turn_left(LEFT)
                await ROBOT.move(40)
                await go_to_next_task()
                door_counter = 0
                prev_prob = 0
                DIRECTION = 'S'
                continue
            else: # completing the task
                await ROBOT.turn_right(RIGHT)
                await ROBOT.move(40)
                await ROBOT.stop()
                await play_complete()
                break
        
        # turning parallel to the wall
        if GOING_FORWARD:
            await ROBOT.turn_left(LEFT)
        else:
            await ROBOT.turn_right(RIGHT)
        if SAVE_DATA:
            sensors = (await ROBOT.get_ir_proximity()).sensors
            write_to_xls(sensors[6], angleDiff, doorprob, wallprob, frameprob)
        prev_prob = prob
        DIRECTION = 'S'

# checks if the robot bumped. readjusts the robot if needed
@event(ROBOT.when_bumped, [True, True])
async def bump(robot):
    global INIT_BUMP, DIRECTION, CORRECTING, GOING_FORWARD, JUST_BUMP, SINGLE_BUMP
    if SINGLE_BUMP:
        return
    await ROBOT.stop()
    SINGLE_BUMP = True
    print('bump')
    await ROBOT.move(-5)
    if not INIT_BUMP:
        INIT_BUMP = True
    else:
        JUST_BUMP = True
        CORRECTING = True
        NETWORK.add_bumper_value(1)

ROBOT.play()
