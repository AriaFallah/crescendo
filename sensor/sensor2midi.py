#!/usr/bin/python

import numpy as np
import rtmidi_python as rtmidi
from time import sleep
from sensor import SensorInterface


def sensor2midi(sensor):
    midi_out = rtmidi.MidiOut()
    midi_out.open_virtual_port("test")

    pitchMatrix = np.zeros(shape=(46, 72))
    for row in xrange(46):
        for col in xrange(72):
            pitchMatrix[row][col] = row * 3

    initialState = sensor.getAllImages()
    while initialState == []:
        initialState = sensor.getAllImages()
        sleep(0.2)
    while True:
        sleep(0.001)
        state = sensor.getAllImages()
        if state:
            diff = np.subtract(initialState[-1]['image'], state[-1]['image'])
            for row, col in np.ndindex(diff.shape):
                if diff[row][col] > 150:
                    pitch = pitchMatrix[row][col]
                    midi_out.send_message([0x90, pitch, 100])
                    sleep(0.01)
                    midi_out.send_message([0x80, pitch, 100])


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
