import serial
import time

ser = serial.Serial("/dev/tty/s0", 115200)

#This script receives and parses GPSdata from a SMS
#Made for Python 2.7 due to legacy gpsd module
#Alexander Stadelmann


#Functionality Check
ser.write("AT")
read = ser.readline()
if read = "OK":
    print("HAT OK")
else:
    raise KeyboardInterrupt("HAT does not reply!")

ser.write("AT+CPIN?")
read = ser.readline()
if read = "+CPIN: READY":
    print "SIM OK"
else:
    raise KeyboardInterrupt("SIM not connected!")

#Tracker SMS check
def SMSCheck():
    while True:
        ser.write "AT+CMGR=1"
        read = ser.readline()
        if "UNREAD" in read:
            print "Unread SMS arrived"
            if "Help me" in read:
                print "SMS is from tracker" 
                message = read
                return message
                break
            else:
                print "SMS is not from tracker, aborting!" 
        time.sleep(20)

#SMS Parser
def SMSParser(SMSCheck()):
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
    coordinates2 = (x2, y2)
    return coordinates2
