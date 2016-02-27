from time import sleep
import myo as libmyo

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
