#Autonomous System (ASYS)
#SMSRecieve + GPSLocationData + Bearing+DistanceCalculator

import serial
import time
import math

ser = serial.Serial("/dev/ttyS0", 115200, timeout=1)
SMSCoords = ""
ObjectiveDistance = 42

class ASYS:
    
    def __init__(self):
        print("Starting.")
        ASYS.PrelaunchChecks(self)
        print("Prelaunch Checks completed.")
        ASYS.SMS(self)
        print("SMS parsed.\nInitiating start up sequence.\n")
        while ObjectiveDistance > 0.01:
            try:
                Calc = ASYS.Calc(self)
            except:
                print("ERROR: Distance and Bearing calculation interrupted.")
                print("Initiating Emergency Stop.")
                print("Attemting to restart.")
            print("Bearing Delta: \t", Calc[0], "deg")
            print("Distance: \t", Calc[1], "km\n") 
            time.sleep(20)
    
    def PrelaunchChecks(self):                           
        while "OK" not in ASYS.SerialCOM(self, "AT"):   #General COM Check
            print("ERROR: Device does not respond.")
            time.sleep(20)
        while "OK" not in ASYS.SerialCOM(self, "AT+CGNSPWR=1"): #GPS Activation
            print("ERROR: GNSS does not respond to power up command")
            time.sleep(20)
        while "READY" not in ASYS.SerialCOM(self, "AT+CPIN?"):  #SIM/GSM Check
            print("ERROR: SIM does not respond.")
            time.sleep(20)
        while "OK" not in ASYS.SerialCOM(self, "AT+CMGF=1"):    #Set MSG Format to Text       
            print("ERROR: GPRS does not respond to changed message format.")
            time.sleep(20)

    def SerialCOM(self, text):                #Communicates Commands
        text = text + "\r\n"
        ser.write(text.encode())
        data = ""
        time.sleep(1)
        while ser.inWaiting() != 0:
            while ser.inWaiting() > 0:
                data += (ser.read(ser.inWaiting())).decode()
        return data

    def GPSInfo(self, bracket):             #Fetches GPS info
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
        deltabearing = bearing - float(GPS[4])
        global ObjectiveDistance
        ObjectiveDistance = distance
        calc = (deltabearing, distance)
        return calc

    def SMSCheck(self):
        while True:
            SMS = ASYS.SerialCOM(self, "AT+CMGL=\"REC UNREAD\"")
            IDText = "Help Me"
            if IDText in SMS:
                print("Unread SMS from tracker received.") 
                SMS = SMS[SMS.find(IDText):len(SMS)]
                return SMS
                break
            time.sleep(20)

    def SMS(self):
        print("SMS Reception activated.")
        message = ASYS.SMSCheck(self).split(",")
        xmessage = message[5]
        ymessage = message[7]
        xmessage1 = xmessage[:-7]
        xmessage2 = xmessage[-7:]
        xmessage2 = float(xmessage2)/60
        x2 = float(xmessage1) + float(xmessage2)
        print("SMS X Coordinates: ", x2)
        ymessage1 = ymessage[:-7]
        ymessage2 = ymessage[-7:]
        ymessage2 = float(ymessage2)/60
        y2 = (float(ymessage1) + float(ymessage2))
        print("SMS Y Coordinates: ", y2)
        global SMSCoords
        SMSCoords = (float(x2), float(y2))
        return SMSCoords
    
    def RTB(self):
        global Coords
        Coords = (47.123442, 8.775506)
        while ObjectiveDistance > 0.01:
            try:
                Calc = ASYS.Calc(self)
            except:
                print("ERROR: Distance and Bearing calculation interrupted.")
                print("Initiating Emergency Stop.")
                print("Attemting to restart.")
            print("Bearing Delta: \t", Calc[0], "deg")
            print("Distance: \t", Calc[1], "km\n") 
            time.sleep(20)


#Launch

ASYS()
