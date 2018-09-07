#Autonomous System (ASYS)
#SMSRecieve + GPSLocationData + Bearing+DistanceCalculator


import serial
import time
import math

ser = serial.Serial("/dev/ttyS0", 115200, timeout=1)

class ASYS:
    
    def __init__(self):

    
    def SerialCOM(self, text):                #Communicates Commands
        text = text + "\r\n"
        ser.write(text)
        data = ""
        time.sleep(2)
        while ser.inWaiting() != 0:
            while ser.inWaiting() > 0:
                data += ser.read(ser.inWaiting())
        return data

    def GPSInfo(self, bracket):                                   #Fetches GPS info
        while "OK" not in SerialCOM("AT+CGNSINF"):              #GPS COM Check
            time.sleep(20)
        while "0" in SerialCOM("AT+CGNSINF").split(",")[1]:     #GPS FIX Check
            time.sleep(20)
        info = SerialCOM("AT+CGNSINF").split(",")[bracket]      #Parsing info
        return info

    def Calc(self):               #Calculates Bearing and Distance
        GPS = GPSInfo(3:4)
        SMS = SMSParser()
        x1 = math.radians(float(GPS[0]))    #fetches longitude from GPS
        y1 = math.radians(float(GPS[1]))    #same, but latitude
        x2 = math.radians(float(SMS[0]))
        y2 = math.radians(float(SMS[1]))
        Deltax = abs(abs(x1)-abs(x2))
        Deltay = abs(abs(y1)-abs(y2))
        x = math.cos(x2) * math.sin(Deltay)
        y = math.cos(x1) * math.sin(x2) - math.sin(x1) * math.cos(x2) * math.cos(abs(abs(y1)-abs(y2)))
        bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
        a = math.pow(math.sin(Deltax/2), 2) + math.cos(x1) * math.cos(x2) * math.pow(math.sin(Deltay / 2), 2) 
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371 * c
        calc = (bearing, distance)
        return calc

    def SMSCheck(self):
        while True:
            SMS = SerialCOM("AT+CMGR=1")
            if "UNREAD" in SMS:
                print("Unread SMS arrived")
            if "Help me" in SMS:
                print("SMS is from tracker") 
                return SMS
                break
            else:
                print("SMS is not from tracker, aborting!")
            time.sleep(20)

    def SMSParser(self):
        print("SMS")
        message = SMSCheck().split(",")
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
        coordinates = (x2, y2)
        return coordinates

    def BearingDelta(self):
        Calc

    def PrelauchChecks(self):                           
        while "OK" not in SerialCOM("AT"):                  #General COM Check
            time.sleep(20)
        while "OK" not in SerialCOM("AT+CGNSPWR=1"):        #GPS Power Activation
            time.sleep(20)
        while "READY" not in SerialCOM("AT+CPOM?"):         #SIM/GSM Check
            time.sleep(20)

#Launch

print("start")
print Calc()
print GPSInfo(7)


