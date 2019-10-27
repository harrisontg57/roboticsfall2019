import easygopigo3
import easysensors
from time import sleep

gobot = easygopigo3.EasyGoPiGo3()
disSen = gobot.init_distance_sensor()
wheelCirc = 208.92 #milimeters
wccm = wheelCirc / 10
f = open("problem1_pathtrace.csv","w+")

#gobot.turn_degrees(180,True)   
    
#takes distance in cm to drive and returns whether the trip was successful.
count = 1
def mkside(d):
    count = 1
    dd = d / wccm
    start = gobot.read_encoders()
    s = gobot.read_encoders_average(units='cm')
    gobot.drive_cm(d + 2)
    while True:
        l = disSen.read_mm()
        f.write(str(count)+","+str(gobot.read_encoders_average())+","+str(disSen.read_mm())+"\n")
        count += 1
        #uppost()
        print(gobot.read_encoders())
        print(gobot.read_encoders_average(units='cm') - s)
        if l < 200:
            gobot.stop()
            return False
        if gobot.read_encoders_average(units='cm') - s >= d:
            gobot.set_speed(0)
            print("Reached Target!")
            return True
        sleep(0.0005)
    

    
#gobot.orbit(-180,0,blocking=True)

f.write("0,"+str(gobot.read_encoders_average())+","+str(disSen.read_mm())+"\n")

route = 1
while True:
    st = gobot.read_encoders()
    if mkside(50):
        print("Made it")
        gobot.set_speed(200)
        gobot.orbit(90*route,0,blocking=True)
    else:
        wlr = gobot.read_encoders()
        w = (wlr[0] + wlr[1])/2
        mv = wlr[0] - st[0]
        print("turning...")
        gobot.set_speed(200)
        #gobot.orbit(180,0,blocking=False)
        gobot.turn_degrees(180)
        print("moving back..")
        gobot.drive_degrees(mv,True)
        
        route = route*-1
        gobot.set_speed(200)
        gobot.orbit(90*route,0,blocking=True)
f.close()