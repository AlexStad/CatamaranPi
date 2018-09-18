# Follow System (FSYS)

import serial
import time
import math


ser = serial.Serial("/dev/ttyS0", 115200, timeout=1)    # Serial Set-up

Coords = ""                     # Variable setting
SMSCoords = ""
ObjectiveDistance = 42


class FSYS:

    def __init__(self):
        print("Follow System initiated.\nStarting Prelaunch Checks.")
        FSYS.PrelaunchChecks(self)
        print("Prelaunch Checks completed")
        FSYS.Mission(self)

    def Mission(self):
        global Coords
        global SMSCoords
        print("Mission started.")
        FSYS.Watch(self)
        print("GPS Tracker reported. Initiating Follow")
        while True:
            FSYS.EXEC(self)

    def EXEC(self):
        global SMSCoords
        global Coords
        while ObjectiveDistance > 0.01:
            try:
                SMS = FSYS.SMS(self)
                if SMS != "":
                    Coords = SMSCoords
                Calc = FSYS.Calc(self)
            except Exception:
                print("ERROR: Distance and Bearing calculation interrupted.")
                print("Initiating Emergency Stop.")
                print("Attemting to restart.")
            print("Bearing Delta: \t", Calc[0], "deg")
            print("Distance: \t", Calc[1], "km\n")

    def PrelaunchChecks(self):
        while "OK" not in FSYS.SerialCOM(self, "AT"):   # General COM Check
            print("ERROR: Device does not respond.")
            time.sleep(20)
        while "OK" not in FSYS.SerialCOM(self, "AT+CGNSPWR=1"):  # GPS Power On
            print("ERROR: GNSS does not respond to power up command")
            time.sleep(20)
        while "READY" not in FSYS.SerialCOM(self, "AT+CPIN?"):  # SIM/GSM Check
            print("ERROR: SIM does not respond.")
            time.sleep(20)
        while "OK" not in FSYS.SerialCOM(self, "AT+CMGF=1"):    # MSG Format
            print("ERROR: GPRS does not respond to changed message format.")
            time.sleep(20)

    def SerialCOM(self, text):                # Communicates Commands
        text = text + "\r\n"
        ser.write(text.encode())
        data = ""
        time.sleep(1)
        while ser.inWaiting() != 0:
            while ser.inWaiting() > 0:
                data += (ser.read(ser.inWaiting())).decode()
        return data

    def GPSInfo(self, bracket):             # Fetches GPS info
        check = "0"
        while check != "1":
            GPS = FSYS.SerialCOM(self, "AT+CGNSINF")
            if "OK" in GPS:              # GPS COM Check
                if "1" in GPS.split(",")[1]:     # GPS FIX Check
                    check = "1"
                else:
                    time.sleep(20)
            else:
                time.sleep(20)
        info = GPS.split(",")[bracket]      # Parsing info
        return info

    def Calc(self):               # Calculates Bearing and Distance
        GPS = FSYS.GPSInfo(self, slice(3, 8))
        x1 = math.radians(float(GPS[0]))    # fetches longitude from GPS
        y1 = math.radians(float(GPS[1]))    # same, but latitude
        x2 = math.radians(float(Coords[0]))
        y2 = math.radians(float(Coords[1]))
        Deltax = abs(abs(x1)-abs(x2))
        Deltay = abs(abs(y1)-abs(y2))
        x = math.cos(x2) * math.sin(Deltay)
        y = math.cos(x1) * math.sin(x2) - math.sin(x1) * math.cos(x2)
        y = y * math.cos(abs(abs(y1)-abs(y2)))
        bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
        a = math.pow(math.sin(Deltax/2), 2) + math.cos(x1) * math.cos(x2)
        a = a * math.pow(math.sin(Deltay / 2), 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371 * c
        deltabearing = bearing - float(GPS[4])
        global ObjectiveDistance
        ObjectiveDistance = distance
        calc = (deltabearing, distance)
        return calc

    def Watch(self):
        print("Watch mode set.")
        count = 0
        while True:
            count += 1
            SMS = FSYS.SerialCOM(self, "AT+CMGL=\"REC UNREAD\"")
            IDText = "Help Me"
            if IDText in SMS:
                print("Unread SMS from tracker received.")
                SMS = SMS[SMS.find(IDText):len(SMS)]
                return SMS
                break
            time.sleep(5)

    def SMS(self):
        SMS = FSYS.SerialCOM(self, "AT+CMGL=\"REC UNREAD\"")
        IDText = "Help Me"
        SMSCoords = ""
        if IDText in SMS:
            SMS = SMS[SMS.find(IDText):len(SMS)]
            message = SMS.split(",")
            xmessage = message[5]
            ymessage = message[7]
            xmessage1 = xmessage[:-7]
            xmessage2 = xmessage[-7:]
            xmessage2 = float(xmessage2)/60
            x2 = float(xmessage1) + float(xmessage2)
            ymessage1 = ymessage[:-7]
            ymessage2 = ymessage[-7:]
            ymessage2 = float(ymessage2)/60
            y2 = (float(ymessage1) + float(ymessage2))
            SMSCoords = (float(x2), float(y2))
        return SMSCoords


# Launch

FSYS()
