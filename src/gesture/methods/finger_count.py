from .fingers import Fingers

class FingerCount():
    def __init__(self):
        super().__init__()
        
    def test(self, landmarks):
        self.thumb = Fingers().ThumbUp(landmarks)
        self.index = Fingers().IndexUp(landmarks)
        self.middle = Fingers().MiddleUp(landmarks)
        self.ring = Fingers().RingUp(landmarks)
        self.pinky = Fingers().PinkyUp(landmarks)

        bool_list = [self.thumb, self.index, self.middle, self.ring, self.pinky]
    
        return bool_list
    
    
    