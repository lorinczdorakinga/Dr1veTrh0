def MiddleUp(self, landmarks):
   # Check if middle tip is above middle pip
        if landmarks["middle_tip"].y < landmarks["middle_pip"].y:
            # Check if middle tip is above other finger tips
            if (landmarks["middle_tip"].y < landmarks["thumb_tip"].y and
                landmarks["middle_tip"].y < landmarks["index_tip"].y and
                landmarks["middle_tip"].y < landmarks["ring_tip"].y and
                landmarks["middle_tip"].y < landmarks["pinky_tip"].y):
                return True
        return False