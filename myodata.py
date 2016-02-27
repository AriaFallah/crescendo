from time import sleep
import myo as libmyo
import rtmidi_python as rtmidi

class Listener(libmyo.DeviceListener):

    #Initialize the midi controller
    #[0xC0, channel (0-127 as DEC), value (0-127 as DEC)]
    midi_out = rtmidi.MidiOut()
    midi_out.open_virtual_port("myo")

    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_orientation_data(self, myo, timestamp, quat):
        roll = quat.roll
        pitch = quat.pitch
        yaw = quat.yaw
        test = round(127 * ((roll + 3.14) / 6.28))
        print test
        self.midi_out.send_message([0xB0, 3, test])

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
