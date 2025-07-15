def PinkyUp(self, landmarks):
        # Check if pinky tip is above pinky pip
        if landmarks["pinky_tip"].y < landmarks["pinky_pip"].y:
            # Check if pinky tip is above other finger tips
            if (landmarks["pinky_tip"].y < landmarks["thumb_tip"].y and
                landmarks["pinky_tip"].y < landmarks["index_tip"].y and
                landmarks["pinky_tip"].y < landmarks["middle_tip"].y and
                landmarks["pinky_tip"].y < landmarks["ring_tip"].y):
                return True
        return False