import math

def calculate_angle(self, p1, p2, p3):
        # Calculate the angle between three points (p1, p2, p3)
        a = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)
        b = math.sqrt((p3.x - p2.x)**2 + (p3.y - p2.y)**2 + (p3.z - p2.z)**2)
        c = math.sqrt((p3.x - p1.x)**2 + (p3.y - p1.y)**2 + (p3.z - p1.z)**2)
        angle = math.acos((a**2 + b**2 - c**2) / (2 * a * b))
        return math.degrees(angle)

def ThumbUp(self, landmarks):
        # Check if thumb tip is above thumb ip
        if landmarks["thumb_tip"].y < landmarks["thumb_ip"].y:
            # Calculate the angle between thumb_mcp, thumb_ip, and thumb_tip
            angle = calculate_angle(self, landmarks["thumb_mcp"], landmarks["thumb_ip"], landmarks["thumb_tip"])
            # Check if the angle is greater than a threshold (e.g., 90 degrees)
            if angle > 90:
                # Check if thumb tip is above other finger tips
                if (landmarks["thumb_tip"].y < landmarks["index_pip"].y and
                    landmarks["thumb_tip"].y < landmarks["middle_pip"].y and
                    landmarks["thumb_tip"].y < landmarks["ring_pip"].y and
                    landmarks["thumb_tip"].y < landmarks["pinky_pip"].y):
                    return True
        return False