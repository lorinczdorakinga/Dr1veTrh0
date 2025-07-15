
def get_hand_landmarks(hand_landmarks, mp_hands):
    return {
        "wrist": hand_landmarks.landmark[mp_hands.HandLandmark.WRIST],
        "thumb_cmc": hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC],
        "thumb_mcp": hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP],
        "thumb_ip": hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP],
        "thumb_tip": hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        "index_mcp": hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP],
        "index_pip": hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP],
        "index_dip": hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP],
        "index_tip": hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
        "middle_mcp": hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP],
        "middle_pip": hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP],
        "middle_dip": hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP],
        "middle_tip": hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
        "ring_mcp": hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP],
        "ring_pip": hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP],
        "ring_dip": hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP],
        "ring_tip": hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
        "pinky_mcp": hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP],
        "pinky_pip": hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP],
        "pinky_dip": hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP],
        "pinky_tip": hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    }