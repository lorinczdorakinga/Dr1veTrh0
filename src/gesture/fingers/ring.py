def RingUp(self, landmarks):
    # Check if ring tip is above ring pip
        if landmarks["ring_tip"].y < landmarks["ring_pip"].y:
            # Check if ring tip is above other finger tips
            if (landmarks["ring_tip"].y < landmarks["thumb_tip"].y and
                landmarks["ring_tip"].y < landmarks["index_tip"].y and
                landmarks["ring_tip"].y < landmarks["middle_tip"].y and
                landmarks["ring_tip"].y < landmarks["pinky_tip"].y):
                return True
        return False