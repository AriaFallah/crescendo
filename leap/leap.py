import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class SampleListener(Leap.Listener):
     
        

    def on_connect(self, controller):
        print "Connected"
 
    def on_frame(self, controller):
        frame = controller.frame()
        hand = frame.hands.rightmost
        hand_cent = hand.palm_position
        handy = hand_cent[1]
        handx = hand_cent[0]
        handz = hand_cent[2]
        mody = round((((handy - 45) / 400) * 127), 0)
        modx = round((((handx + 150) / 300) * 127), 0)
        modz = round((((handz + 150) / 300) * 127), 0)
        if mody > 127:
            mody = 127
        if mody < 0:
            mody = 0
        if modx > 127:
            modx = 127
        if modx < 0:
            modx = 0
        if modz > 127:
            modz = 127
        if modz < 0:
            modz = 0
        if hand.time_visible == 0:
            print "Hand not visible"
        else:
            print mody, modx, modz

def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.add_listener(listener)
    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)
if __name__ == "__main__":
    main()
