from time import sleep
import myo as libmyo
import rtmidi_python as rtmidi

class Listener(libmyo.DeviceListener):

    midi_out = None

    def __init__(self, midi_out):
        self.midi_out = midi_out

    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_orientation_data(self, myo, timestamp, quat):
        roll = round(127 * ((quat.roll + 3.14) / 6.28))
        pitch = round(127 * ((quat.pitch + 3.14) / 6.28))
        yaw = round(127 * ((quat.yaw + 3.14) / 6.28))
        print "%d x %d x %d" % (roll, pitch, yaw)
        self.midi_out.send_message([0xB0, 3, roll])
        self.midi_out.send_message([0xB0, 9, pitch])
        self.midi_out.send_message([0xB0, 14, yaw])

#Initialize the midi controller
#[0xC0, channel (0-127 as DEC), value (0-127 as DEC)]
midi_out = rtmidi.MidiOut()
midi_out.open_virtual_port("myo")

#Initialize the libmyo controller
libmyo.init("myo.framework")
hub = libmyo.Hub()
myoListener = Listener(midi_out)
hub.run(1000, myoListener)

try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    print "Quit"
finally:
    hub.shutdown()
