import numpy as np

def IndexUp(self, landmarks):
    # Check if index tip is above index pip
        if landmarks["index_tip"].y < landmarks["index_pip"].y:
            # Check if index tip is above other finger tips
            if (landmarks["index_tip"].y < landmarks["thumb_tip"].y and
                landmarks["index_tip"].y < landmarks["middle_tip"].y and
                landmarks["index_tip"].y < landmarks["ring_tip"].y and
                landmarks["index_tip"].y < landmarks["pinky_tip"].y):
                return True
        return False