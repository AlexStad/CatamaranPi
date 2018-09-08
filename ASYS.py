#Autonomous System (ASYS)
#SMSRecieve + GPSLocationData + Bearing+DistanceCalculator


import serial
import time
import math

ser = serial.Serial("/dev/ttyS0", 115200, timeout=1)
SMSCoords = ""
ObjectiveDistance = 1701

class ASYS:
    
    def __init__(self):
        print("Starting...")
        ASYS.PrelaunchChecks(self)
        print("Prelaunch Checks completed.")
        ASYS.SMS(self)
        print("SMS received and parsed. Initiating start up.")
        while Distance > 20:
            start_time = time.time()
            print(ASYS.Calc(self))
            print("--- %s seconds ---" % (time.time() - start_time))
            time.sleep(20)
            
        
    
    def PrelaunchChecks(self):                           
        while "OK" not in ASYS.SerialCOM(self, "AT"):                  #General COM Check
            time.sleep(20)
        while "OK" not in ASYS.SerialCOM(self, "AT+CGNSPWR=1"):        #GPS Power Activation
            time.sleep(20)
        print("yep")
        while "READY" not in ASYS.SerialCOM(self, "AT+CPIN?"):         #SIM/GSM Check
            time.sleep(20)

    def SerialCOM(self, text):                #Communicates Commands
        text = text + "\r\n"
        ser.write(text.encode())
        data = ""
        time.sleep(2)
        while ser.inWaiting() != 0:
            while ser.inWaiting() > 0:
                data += (ser.read(ser.inWaiting())).decode()
        return data

    def GPSInfo(self, bracket):                                   #Fetches GPS info
        check = "0"
        while check != "1":
            GPS = ASYS.SerialCOM(self, "AT+CGNSINF")
            if "OK" in GPS:              #GPS COM Check
                if "1" in GPS.split(",")[1]:     #GPS FIX Check
                    check = "1"
                else:
                    time.sleep(20)
            else:
                time.sleep(20)
        info = GPS.split(",")[bracket]      #Parsing info

        return info

    def Calc(self):               #Calculates Bearing and Distance
        GPS = ASYS.GPSInfo(self, slice(3,8))
        x1 = math.radians(float(GPS[0]))    #fetches longitude from GPS
        y1 = math.radians(float(GPS[1]))    #same, but latitude
        x2 = math.radians(float(SMSCoords[0]))
        y2 = math.radians(float(SMSCoords[1]))
        Deltax = abs(abs(x1)-abs(x2))
        Deltay = abs(abs(y1)-abs(y2))
        x = math.cos(x2) * math.sin(Deltay)
        y = math.cos(x1) * math.sin(x2) - math.sin(x1) * math.cos(x2) * math.cos(abs(abs(y1)-abs(y2)))
        bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
        a = math.pow(math.sin(Deltax/2), 2) + math.cos(x1) * math.cos(x2) * math.pow(math.sin(Deltay / 2), 2) 
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371 * c
        deltabearing = bearing - GPS[4]
        global ObjectiveDistance
        ObjectiveDistance = distance
        calc = (deltabearing, distance)
        return calc

    def SMSCheck(self):
        while True:
            SMS = ASYS.SerialCOM(self, "AT+CMGR=1")
            if "UNREAD" in SMS:
                print("Unread SMS arrived")
                if "Help me" in SMS:
                    print("SMS is from tracker") 
                    return SMS
                    break
                else:
                    print("SMS is not from tracker, aborting!")
            time.sleep(20)

    def SMS(self):
        print("SMS")
        message = ASYS.SMSCheck(self).split(",")
        print(message)
        xmessage = message[5]
        ymessage = message[7]
        xmessage1 = xmessage[0:1]
        xmessage2 = xmessage[2:6]
        xmessage2 = float(xmessage2)/60
        x2= float(xmessage1 + "." + xmessage2)
        print(x2)
        ymessage1 = ymessage[0:1]
        ymessage2 = ymessage[2:6]
        ymessage2 = float(ymessage2)/60
        y2= float(ymessage1 + "." + ymessage2)
        print(y2)
        global SMSCoords
        SMSCoords = (x2, y2)
        return SMSCoords


#Launch

ASYS()
