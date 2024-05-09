from collections import deque

class MovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
    
    def add_value(self, value):
        self.values.append(value)
    
    def get_mean(self):
        if len(self.values) == 0:
            return None
        return sum(self.values) / len(self.values)