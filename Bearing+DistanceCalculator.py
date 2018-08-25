#Calculates the bearing and distance between two GPS coordinates
#Alexander Stadelmann

import math

#Bearing Calculation:

x1 = math.radians(float(input("Enter the X coordinates of Point 1: ")))
y1 = math.radians(float(input("Enter the y coordinates of Point 1: ")))
x2 = math.radians(float(input("Enter the x coordinates of Point 2: ")))
y2 = math.radians(float(input("Enter the y coordinates of Point 2: ")))
Deltax = abs(abs(x1)-abs(x2))
Deltay = abs(abs(y1)-abs(y2))
x = math.cos(x2) * math.sin(Deltay)
y = math.cos(x1) * math.sin(x2) - math.sin(x1) * math.cos(x2) * math.cos(abs(abs(y1)-abs(y2)))
bearing = (math.degrees(math.atan2(x, y)) + 360) % 360

print(bearing)

#Distance Calculation (Haversine Formula)

a = math.pow(math.sin(Deltax/2), 2) + math.cos(x1) * math.cos(x2) * math.pow(math.sin(Deltay / 2), 2) 
c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
distance = 6371 * c
print(distance)

