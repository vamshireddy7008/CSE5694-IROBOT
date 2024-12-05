# https://github.com/iRobotEducation/irobot-edu-python-sdk

# run "pip3 install irobot_edu_sdk"
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
from irobot_BN3 import IrobotNetwork as IRN
from XWrite import writer
import time

print("Starting Irobot")

connected = False
while not connected:
    try:
        ROBOT = Create3(Bluetooth())
        connected = True
    except:
        print('failed to connect retrying')
NETWORK = IRN()

WALL_AVG = NETWORK.NetworkSet['Wall_Nodes']['scanner'].normal_dist.mean
WALL_STD_DEV = NETWORK.NetworkSet['Wall_Nodes']['scanner'].normal_dist.sd

DOOR_AVG = NETWORK.NetworkSet['Door_Nodes']['scanner'].normal_dist.mean
DOOR_STD_DEV = NETWORK.NetworkSet['Door_Nodes']['scanner'].normal_dist.sd

FRAME_AVG = NETWORK.NetworkSet['Frame_Nodes']['scanner'].normal_dist.mean
FRAME_STD_DEV = NETWORK.NetworkSet['Frame_Nodes']['scanner'].normal_dist.sd

BASE_ANGLE = 0

INIT_SPEED = 4
SPEED = 12

INTERVAL = 1

INIT_BUMP = False

JUST_BUMP = False

SINGLE_BUMP = False

CORRECTING = False

DIRECTION = 'T' # S == Stright, T == Turn

GOING_FORWARD = True

QUARTER_NOTE_LENGTH = 0.3

SAVE_DATA = True

PENDING_TURNAROUND = -1

DATA_WRITE = None
if SAVE_DATA:
    DATA_WRITE = writer()

CANT_BE_DOOR = 0

# goes to the next task
async def go_to_next_task():
    global ROBOT, GOING_FORWARD, QUARTER_NOTE_LENGTH, BASE_ANGLE
    GOING_FORWARD = False
    #await ROBOT.turn_right(90)
    #await reset_robot_direction(175, 10)
    #await ROBOT.turn_right(90)
    await ROBOT.turn_right(180)

    BASE_ANGLE = (await ROBOT.get_position()).heading

def angle_difference(frst, scnd):
    value = frst - scnd
    output = 0
    if value > 180:
        output = value - 360
    elif value < -180:
        output = value + 360
    else:
        output = value
    if output < 0:
        return - output
    return output

def write_to_xls(sensors, angle):
    global NETWORK, JUST_BUMP, DATA_WRITE
    prob_door = NETWORK.calculate_probability(type= 'door', time = 1)
    prob_wall = NETWORK.calculate_probability(type= 'wall', time = 1)
    prob_frame = NETWORK.calculate_probability(type= 'frame', time = 1)
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
    global INIT_BUMP, BASE_IR_SENSOR, INIT_SPEED, BASE_ANGLE, ROBOT
    await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    while not INIT_BUMP:
        await ROBOT.move(5)
        time.sleep(0.3)
    await ROBOT.stop()
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

# fixes the robot direction
async def reset_robot_direction(mean = 400, stdD = 40):
    global INIT_BUMP, BASE_IR_SENSOR, ROBOT, INIT_SPEED, SPEED, WALL_AVG, WALL_STD_DEV
    await ROBOT.set_wheel_speeds(INIT_SPEED,INIT_SPEED)
    INIT_BUMP = False
    await initiate_robot()
    sensors = (await ROBOT.get_ir_proximity()).sensors
    await fix_robot_direction(mean, stdD)
    BASE_IR_SENSOR = sensors[3]
    print(BASE_IR_SENSOR)

async def fix_robot_direction(value, threshold):    
    global INIT_BUMP, BASE_IR_SENSOR, ROBOT
    await initiate_robot()
    sensors = (await ROBOT.get_ir_proximity()).sensors
    while sensors[3] - value > threshold or sensors[3] - value < -1 * threshold:
        if sensors[3] > value:
            await ROBOT.set_wheel_speeds(-1,-1)
        else:
            await ROBOT.set_wheel_speeds(1,1)
        sensors = (await ROBOT.get_ir_proximity()).sensors
    await ROBOT.stop()
    print(BASE_IR_SENSOR)

async def get_sensor_value():
    global GOING_FORWARD
    if GOING_FORWARD:
        return (await ROBOT.get_ir_proximity()).sensors[6]
    else:
        return (await ROBOT.get_ir_proximity()).sensors[0] - 25


@event(ROBOT.when_play)
async def play(robot):
    global SPEED, CORRECTING, DIRECTION, SAVE_DATA, GOING_FORWARD, SINGLE_BUMP, BASE_ANGLE, ROBOT, CANT_BE_DOOR, PENDING_TURNAROUND
    global WALL_AVG, WALL_STD_DEV, DOOR_AVG, DOOR_STD_DEV, FRAME_AVG, FRAME_STD_DEV, INTERVAL

    directional_counter = 0
    
    door_counter = 0
    prev_prob = 0
    lspeed = SPEED
    rspeed = SPEED
    #prevSenVal = 80
    prevError = 0
    error = 0
    derivative = 0
    adjustment = 0
    
    close_factor = 0
    rescan = False
    
    await initiate_robot()
    await fix_robot_direction(470, 40)

    sensors = (await ROBOT.get_ir_proximity()).sensors
    await ROBOT.turn_left(90)
    DIRECTION = 'S'
    print('start walk')
    BASE_ANGLE = (await ROBOT.get_position()).heading

    sensor_value = await get_sensor_value()
    NETWORK.add_scanner_value(sensor_value)
    NETWORK.add_bumper_value(0)
    NETWORK.add_wheel_value(0)
    doorprob = NETWORK.calculate_probability(type = 'door', time = 1)
    wallprob = NETWORK.calculate_probability(type = 'wall', time = 1)
    frameprob = NETWORK.calculate_probability(type = 'frame', time = 1)
    probability = 0
    base_value = WALL_AVG
    base_high = WALL_AVG + WALL_STD_DEV
    base_low = WALL_AVG - WALL_STD_DEV
    CANT_BE_DOOR = 10
    await ROBOT.set_wheel_speeds(lspeed,rspeed)
    nextTime = time.time() + INTERVAL
    while True:
        SINGLE_BUMP = False
        if CORRECTING:
            print("correcting")
            await initiate_robot()
            await ROBOT.move(-5)
            if GOING_FORWARD:
                await ROBOT.turn_left(30)
            else:
                await ROBOT.turn_right(30)
            CORRECTING = False

        sensor_value = await get_sensor_value()
        if time.time() >= nextTime or rescan:
            rescan = False
            if CANT_BE_DOOR <= 0 :
                NETWORK.add_scanner_value(sensor_value)
                NETWORK.add_bumper_value(0)
                angleDiff = angle_difference((await ROBOT.get_position()).heading, BASE_ANGLE)
                NETWORK.add_wheel_value(angleDiff)
                doorprob = NETWORK.calculate_probability(type = 'door', time = 1)
                wallprob = NETWORK.calculate_probability(type = 'wall', time = 1)
                frameprob = NETWORK.calculate_probability(type = 'frame', time = 1)
                probability = NETWORK.calculate_probability(type = 'door')
                if SAVE_DATA:
                    write_to_xls(sensor_value,angleDiff)
                nextTime = time.time() + INTERVAL
                if PENDING_TURNAROUND >= 0:
                    print("pending " + str(PENDING_TURNAROUND))
                    if PENDING_TURNAROUND == 0:
                        await ROBOT.stop()
                        await ROBOT.set_wheel_speeds(0,0)
                        if GOING_FORWARD:
                            await go_to_next_task()
                        else:
                            break
                        CANT_BE_DOOR = 0
                    PENDING_TURNAROUND -= 1
            elif CANT_BE_DOOR == 1:
                BASE_ANGLE = (await ROBOT.get_position()).heading
        print(sensor_value)
        if doorprob > 0.5 and CANT_BE_DOOR <= 0:
            base_value = DOOR_AVG
            print('door')
            base_std_d = DOOR_STD_DEV
        elif wallprob > 0.5 or CANT_BE_DOOR > 0:
            base_value = WALL_AVG
            print('wall')
            base_std_d = WALL_STD_DEV
        elif frameprob > 0.5:
            base_value = FRAME_AVG
            base_std_d = FRAME_STD_DEV
            print('frame')
        if CANT_BE_DOOR > 0:
            print('cant be door')
            CANT_BE_DOOR -= 1
        close_factor = 0
        for val in sensors:
            if val > 200:
                close_factor = 2
            if val > 450:
                close_factor = 4
                break
        
        error = sensor_value - base_value
        derivative = error - prevError
        adjustment = (derivative + error)/ (2.0 * base_std_d)
        if adjustment > 0.75:
            adjustment = 0.75
        elif adjustment < -1.5:
            adjustment = -1.5
        print('adj: '+ str(adjustment))
        prevError = error

        lspeed = SPEED - close_factor + adjustment
        rspeed = SPEED - close_factor - adjustment

        if GOING_FORWARD:
            await ROBOT.set_wheel_speeds(rspeed,lspeed)
        else:
            await ROBOT.set_wheel_speeds(lspeed,rspeed)
        
        if sensor_value > 1.25 * base_high or sensor_value < 0.75 * base_low:
            rescan = True

        if prev_prob > 0.5 and probability < 0.4:
            door_counter += 1
            CANT_BE_DOOR = 20
            NETWORK.remove_bump()
            NETWORK.remove_scanner()
            base_value = WALL_AVG
            base_high = WALL_AVG + WALL_STD_DEV
            base_low = WALL_AVG - WALL_STD_DEV  
            await ROBOT.play_note(Note.A5, 0.20)
            print("door counter: " + str(door_counter))
            if door_counter == 3:
                door_counter = 0
                PENDING_TURNAROUND = 3
                CANT_BE_DOOR = 0
                base_value = DOOR_AVG
                base_high = DOOR_AVG + DOOR_STD_DEV
                base_low = DOOR_AVG - DOOR_STD_DEV 
                
        prev_prob = probability
        time.sleep(0.1)
        

# checks if the robot bumped. readjusts the robot if needed
@event(ROBOT.when_bumped, [True, True])
async def bump(robot):
    global INIT_BUMP, DIRECTION, CORRECTING, GOING_FORWARD, JUST_BUMP, SINGLE_BUMP
    if not INIT_BUMP:
        INIT_BUMP = True
    else:
        JUST_BUMP = True
        CORRECTING = True
        NETWORK.add_bumper_value(1)
    await ROBOT.stop()
    await ROBOT.set_wheel_speeds(-1,-1)
    if SINGLE_BUMP:
        return
    SINGLE_BUMP = True
    print('bump')
    await ROBOT.move(-5)

ROBOT.play()
