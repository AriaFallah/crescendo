#!/usr/bin/python

import numpy as np
import rtmidi_python as rtmidi
import threading
from time import sleep
from sensor import SensorInterface

# The dimensions of the board
BOARD_ROWS = 46
BOARD_COLS = 72


class Board:
    def __init__(self, numRegions):
        print 'initializing...'

        # Create a virtual MIDI device
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_virtual_port("TouchPad")

        self.activeRegions = []
        self.numRegions = numRegions
        self.sensor = SensorInterface()
        self.pitches = []
        self.modulo = BOARD_COLS / numRegions

        for x in xrange(numRegions + 1):
            thread = threading.Thread(target=self.handleTouch, args=(x,))
            thread.daemon = True
            thread.start()

        try:
            self.create_regions(numRegions)
        except:
            raise

        try:
            self.sensor.connect()
        except:
            raise

    def create_regions(self, numRegions):
        # Make sure the number divides the board evenly
        if numRegions not in [1, 2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72]:
            raise Exception("Valid number of regions is one of the following [1, 2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72]")

        # Fill the matrix with proper pitches
        x = 30
        self.modulo = BOARD_COLS / numRegions
        for col in xrange(BOARD_COLS):
            self.pitches.append(x)
            if col % self.modulo == 0:
                x = x + self.modulo

    def sensor2midi(self):
        # Read initial state until it's not empty
        initialState = []
        while initialState == []:
            initialState = self.sensor.getAllImages()
            sleep(0.2)

        print "ready!"

        # Observe touch events
        while True:
            sleep(0.01)
            state = self.sensor.getAllImages()
            if state:
                # Diff the initial state with the new state
                diff = np.subtract(initialState[-1]['image'], state[-1]['image'])
                self.activeRegions = np.unique(np.where(diff > 100)[1] // self.modulo)

    def handleTouch(self, region):
        active = False
        while True:
            sleep(0.01)
            if region in self.activeRegions and not active:
                active = True
                pitch = self.pitches[region * self.modulo]
                self.midi_out.send_message([0x90, pitch, 100])
            elif region not in self.activeRegions and active:
                self.midi_out.send_message([0x80, pitch, 100])
                active = False


def main():
    board = Board(72)
    board.sensor2midi()


if __name__ == '__main__':
    main()
