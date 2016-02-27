#!/usr/bin/python

import numpy as np
from time import sleep
from sensor import SensorInterface


def sensor2midi(sensor):
    initialState = sensor.getAllImages()
    while initialState == []:
        initialState = sensor.getAllImages()
        sleep(0.2)
    while True:
        sleep(0.001)
        print ("")
        state = sensor.getAllImages()
        if state:
            diff = np.subtract(initialState[-1]['image'], state[-1]['image'])
            for row, col in np.ndindex(diff.shape):
                if diff[row][col] > 10:
                    print ("TOUCH")


def Main():
    sensor = SensorInterface()
    try:
        sensor.connect()
    except:
        print("Error connecting to sensor")
        raise
        return

    sensor2midi(sensor)
    sensor.close()

if __name__ == '__main__':
    Main()
