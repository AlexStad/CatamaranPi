# Autonomous System (ASYS)
# SMSRecieve + GPSLocationData + Bearing+DistanceCalculator

import serial
import time
import math


ser = serial.Serial("/dev/ttyS0", 115200, timeout=1)    # Serial Set-up

Coords = ""                     # Variable setting
TurnCoords = ""
SMSCoords = ""
ObjectiveDistance = 42

X1 = round(47.129780, 4)    # Routing line coordinates
Y1 = round(8.781155, 4)     # Only in middle of Sihlsee!
X2 = round(47.101284, 4)
Y2 = round(8.796171, 4)
DeltaX = X2-X1              # GPSLine List Calculations
DeltaY = Y2-Y1
DivX = -0.0001
DivY = (DeltaY/DeltaX) * DivX
GPSXList = []
GPSYList = []
X = X1
Y = Y1
count = 0
while count != 536:
    X = round(X1+(DivX*count), 4)
    Y = round(Y1+(DivY*count), 4)
    GPSXList.append(X)
    GPSYList.append(Y)
    count += 1


class ASYS:

    def __init__(self):
        print("Autonomous System initiated.\nStarting Prelaunch Checks.")
        ASYS.PrelaunchChecks(self)
        print("Prelaunch Checks completed")
        print("Setting Stand-By Position coordinates.")
        ASYS.StandBy(self)
        print("Arrived at Stand-By position.\nStarting Mission.")
        while True:
            ASYS.Mission(self)
            "Checking for RTB command."
            if ASYS.RTBCheck(self):
                break
            else:
                print("No RTB command recieved")
        print("Setting Base coordinates.")
        ASYS.RTB(self)

    def Mission(self):
        global Coords
        global SMSCoords
        global TurnCoords
        print("Mission started.")
        ASYS.SMS(self)
        print("SMS parsed.\nRouting.\n")
        ASYS.Routing(self, SMSCoords[0], SMSCoords[1])
        Coords = TurnCoords
        print("GPS Routed.\nInitiating approach to turn point.")
        ASYS.EXEC(self)
        print("Turn point reached. Setting final approach coordinates.")
        Coords = SMSCoords
        print("Final approach coordinates set.\nInitiating final approach.")
        ASYS.EXEC(self)
        print("Arrived at destination. Entering sleep mode.")
        input("Press enter to exit sleep mode.")
        print("Sleep mode exit initiated.")
        print("2 Minutes until Return to Stand-By Position.")
        time.sleep(120)
        Coords = TurnCoords
        print("GPS Routed.\nInitiating approach to turn point.")
        ASYS.EXEC(self)
        print("Turn point reached.\nSetting Stand-By Position coordinates.")
        ASYS.StandBy(self)
        print("Arrived at Stand-By position.\nRestarting Mission.")

    def EXEC(self):
        while ObjectiveDistance > 0.01:
            try:
                Calc = ASYS.Calc(self)
            except Exception:
                print("ERROR: Distance and Bearing calculation interrupted.")
                print("Initiating Emergency Stop.")
                print("Attemting to restart.")
            print("Bearing Delta: \t", Calc[0], "deg")
            print("Distance: \t", Calc[1], "km\n")
            time.sleep(20)

    def PrelaunchChecks(self):
        while "OK" not in ASYS.SerialCOM(self, "AT"):   # General COM Check
            print("ERROR: Device does not respond.")
            time.sleep(20)
        while "OK" not in ASYS.SerialCOM(self, "AT+CGNSPWR=1"):  # GPS Power On
            print("ERROR: GNSS does not respond to power up command")
            time.sleep(20)
        while "READY" not in ASYS.SerialCOM(self, "AT+CPIN?"):  # SIM/GSM Check
            print("ERROR: SIM does not respond.")
            time.sleep(20)
        while "OK" not in ASYS.SerialCOM(self, "AT+CMGF=1"):    # MSG Format
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
            GPS = ASYS.SerialCOM(self, "AT+CGNSINF")
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
        GPS = ASYS.GPSInfo(self, slice(3, 8))
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
            SMS = ASYS.SerialCOM(self, "AT+CMGL=\"REC UNREAD\"")
            IDText = "Help Me"
            if IDText in SMS:
                print("Unread SMS from tracker received.")
                SMS = SMS[SMS.find(IDText):len(SMS)]
                return SMS
                break
            if count == 31:         # Returns to Stand By Position every 10 min
                ASYS.StandBy(self)
                count = 0
            time.sleep(20)

    def SMS(self):
        print("Setting Watch mode.")
        message = ASYS.Watch(self).split(",")
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

    def Routing(self, X1, Y1):
        X1 = round(X1, 4)
        Y1 = round(Y1, 4)
        global GPSXList
        global GPSYList
        if X1 in GPSXList:
            global TurnCoords
            TurnCoords = (X1, GPSYList[GPSXList.index(X1)])
            return TurnCoords
        else:
            print("ERROR: Goal Coordinates not in operation Range!")

    def RTBCheck(self):
        Command = False
        SMS = ASYS.SerialCOM(self, "AT+CMGL=\"REC UNREAD\"")
        IDText = "RTB!"
        if IDText in SMS:
            print("RTB Command received.")
            Command = True
        return Command

    def RTB(self):                     # Return to Base
        global Coords
        Coords = (47.123442, 8.775506)  # coordinates of the catamaran's base
        print("Base coordinates set.\nInitiating approach.")
        ASYS.EXEC(self)
        print("Catamaran arrived at base.")
        print("Autonomous System shutting down.")

    def StandBy(self):                 # StandBy at the middle of the lake
        global Coords
        Coords = (47.120697, 8.786875)  # coordinates of the middle of the lake
        print("Stand-By coordinates set.\nInitiating approach.")
        ASYS.EXEC(self)


# Launch

ASYS()
