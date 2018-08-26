from gps import *
import time
import threading


gpsd = None                             #sets global variable

class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd                     #bring in scope
        gpsd = gps(mode=WATCH_ENABLE)   #starting stream of info
        self.current_value = None
        self.running = True             #setting thread running to true


def GPS():
    global gpsp
    gpsp = GpsPoller()                  #create thread
    gpsp.start()                        #start up
    counter=0
    while gpsd.fix.mode < 2:            #ensures 3D fix
        time.sleep(3)
        counter+=1
        if counter > 5:
            gpsp.running = False
            gpsp.join()
            break
    xcoordinates = float(gpsd.fix.latitude)
    ycoordinates = float(gpsd.fix.longitude)
    track = float(gpsd.fix.track)
    gpsp.running = False
    gpsp.join()                         #wait for thread to finish
    gps = (xcoordinates, ycoordinates, track)
    return gps

print(GPS()[0])
print(GPS()[1])
print(GPS()[2])
