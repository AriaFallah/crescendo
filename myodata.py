from time import sleep
import myo as libmyo
import rtmidi_python as rtmidi

#Midi channels for the three different types of motion
roll_channel = 3
pitch_channel = 9
yaw_channel = 14

class Listener(libmyo.DeviceListener):

    midi_out = None

    def __init__(self, midi_out, roll_channel, pitch_channel, yaw_channel):
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
        self.midi_out.send_message([0xB0, roll_channel, roll])
        self.midi_out.send_message([0xB0, pitch_channel, pitch])
        self.midi_out.send_message([0xB0, yaw_channel, yaw])

#Initialize the midi controller
#[0xC0, channel (0-127 as DEC), value (0-127 as DEC)]
midi_out = rtmidi.MidiOut()
midi_out.open_virtual_port("myo")

#Assign the channels
result = raw_input("Assigning roll: Set the application to listen to controller input. Press Enter to continue (or s to skip).\n")
if result != "s":
    midi_out.send_message([0xB0, roll_channel, 0])

result = raw_input("Assigning pitch: Set the application to listen to controller input. Press Enter to continue (or s to skip).\n")
if result != "s":
    midi_out.send_message([0xB0, pitch_channel, 0])

result = raw_input("Assigning yaw: Set the application to listen to controller input. Press Enter to continue (or s to skip).\n")
if result != "s":
    midi_out.send_message([0xB0, yaw_channel, 0])

#Initialize the libmyo controller
libmyo.init("myo.framework")
hub = libmyo.Hub()
myoListener = Listener(midi_out, roll_channel, pitch_channel, yaw_channel)
hub.run(1000, myoListener)

try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    print "Quit"
finally:
    hub.shutdown()
