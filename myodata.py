from time import sleep
import myo as libmyo
import rtmidi_python as rtmidi

class Listener(libmyo.DeviceListener):

    roll = 0
    pitch = 0
    yaw = 0

    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_orientation_data(self, myo, timestamp, quat):
        roll = quat.roll
        pitch = quat.pitch
        yaw = quat.yaw

#Initialize the midi controller
#[0xC0, channel (0-127 as DEC), value (0-127 as DEC)]
midi_out = rtmidi.MidiOut()
midi_out.open_virtual_port("myo")

#Initialize the libmyo controller
libmyo.init("myo.framework")
hub = libmyo.Hub()
myoListener = Listener()
hub.run(1000, myoListener)

try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    print "Quit"
finally:
    hub.shutdown()
