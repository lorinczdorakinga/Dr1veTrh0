import numpy as np
import math

class Fingers():
    def __init__(self):
        pass

    def ThumbUp(self, landmarks):
        # Check if thumb tip is above thumb ip
        difference = abs(landmarks["thumb_tip"].y - landmarks["thumb_ip"].y)
        # print(difference)
        #if landmarks["thumb_tip"].y < landmarks["thumb_ip"].y:
        if difference > 0.045:
                    return True
        return False

    def IndexUp(self, landmarks):
    # Check if index tip is above index pip
        if landmarks["index_tip"].y < landmarks["index_pip"].y:
            return True
        return False
    
    def MiddleUp(self, landmarks):
   # Check if middle tip is above middle pip
        if landmarks["middle_tip"].y < landmarks["middle_pip"].y:
            return True
        return False
    
    def RingUp(self, landmarks):
    # Check if ring tip is above ring pip
        if landmarks["ring_tip"].y < landmarks["ring_pip"].y:
            return True
        return False
    
    def PinkyUp(self, landmarks):
        # Check if pinky tip is above pinky pip
        if landmarks["pinky_tip"].y < landmarks["pinky_pip"].y:
            return True
        return False