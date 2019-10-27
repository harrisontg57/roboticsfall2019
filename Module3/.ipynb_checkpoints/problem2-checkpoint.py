from di_sensors import inertial_measurement_unit
from easygopigo3 import *
from math import *
from statistics import mean
from time import sleep

def getNorthPoint(imu):
    """
    Determines the heading of the north point.
    This function doesn't take into account the declination.

    :param imu: It's an InertialMeasurementUnit object.
    :return: The heading of the north point measured in degrees. The north point is found at 0 degrees.

    """

    x, y, z = imu.read_magnetometer()

    # using the x and z axis because the sensor is mounted vertically
    # the sensor's top face is oriented towards the back of the robot
    heading = -atan2(x, -z) * 180 / pi

    # adjust it to 360 degrees range
    if heading < 0:
        heading += 360
    elif heading > 360:
        heading -= 360

    # when the heading is towards the west the heading is negative
    # when the heading is towards the east the heading is positive
    if 180 < heading <= 360:
        heading -= 360

    #heading += MAGNETIC_DECLINATION

    return heading


def orientate():
    
    
    try:
        imu = inertial_measurement_unit.InertialMeasurementUnit(bus = "GPG3_AD1")
    except Exception as msg:
        print(str(msg))
    
    print("Rotate the GoPiGo3 robot with your hand until it's fully calibrated")
    try:
        compass = imu.BNO055.get_calibration_status()[3]
    except Exception as msg:
        compass = 0
    values_already_printed = []
    max_conseq_errors = 3

    while compass != 3:
        state = ""
        if compass == 0:
            state = "not yet calibrated"
        elif compass == 1:
            state = "partially calibrated"
        elif compass == 2:
            state = "almost calibrated"

        if not compass in values_already_printed:
            print("The GoPiGo3 is " + state)
        values_already_printed.append(compass)

        try:
            compass = imu.BNO055.get_calibration_status()[3]
        except Exception as msg:
            max_conseq_errors -= 1
            sleep(0.09)
            continue
    
    print("The GoPiGo3 is Calibrated")
    return imu

f = open("problem2_pathtrace.csv","w+")
newTurn = 0
orr = ['N','E','S','W']
count = 1
def mkside(d):
    count = 1
    dd = d / wccm
    start = gobot.read_encoders()
    s = gobot.read_encoders_average(units='cm')
    gobot.drive_cm(d + 2)
    while True:
        l = disSen.read_mm()
        #uppost()
        f.write(str(count)+","+str(gobot.read_encoders_average())+","+str(disSen.read_mm())+","+orr[newTurn]+"\n")
        count += 1
        print(gobot.read_encoders())
        print(gobot.read_encoders_average(units='cm') - s)
        if l < 200:
            gobot.stop()
            return d - (gobot.read_encoders_average(units='cm') - s) #distance left to travel
        if gobot.read_encoders_average(units='cm') - s >= d:
            gobot.set_speed(0)
            print("Reached Target!")
            return 0
        sleep(0.0005)

    
        
gobot = EasyGoPiGo3()
disSen = gobot.init_distance_sensor()
wheelCirc = 208.92 #milimeters
wccm = wheelCirc / 10
imu = orientate()
print("place on ground in 2 seconds")
sleep(2)

np = getNorthPoint(imu)
f.write(str(0)+","+str(gobot.read_encoders_average())+","+str(disSen.read_mm())+","+orr[newTurn]+"\n")
print(np)

    
gobot.orbit(-np,0,blocking=True)

size = 50
while True:
    st = gobot.read_encoders()
    remaining = mkside(size)
    print(remaining)
    print(newTurn)
    if remaining == 0:
        print("Made it")
        np = getNorthPoint(imu)
        gobot.set_speed(300)
        if newTurn == 0:
            np = (getNorthPoint(imu) + np)/2 
            gobot.orbit(90-np,0,blocking=True)
            newTurn += 1
            continue
        elif newTurn == 1:
            np = (getNorthPoint(imu) + np)/2
            gobot.orbit(180-np,0,blocking=True)
            newTurn += 1
            continue
        elif newTurn == 2:
            np = (getNorthPoint(imu) + np)/2
            gobot.orbit(90-(180-np),0,blocking=True)
            newTurn += 1
            continue
        elif newTurn == 3:
            np = (getNorthPoint(imu) + np)/2
            gobot.orbit(180 + np,0,blocking=True)
            newTurn = 0
            continue
    else:
        gobot.orbit(-90,0,blocking=True)
        gobot.orbit(180,10,blocking=True)
        gobot.orbit(-90,0,blocking=True)
        gobot.drive_cm(remaining-20)
        gobot.orbit(90,0,blocking=True)
        print()