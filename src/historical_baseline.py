class HistoricalBaseline:
    def __init__(self):
        self.baseline = None
        self.peak = None
        self.history = []
    
    def add_frame_data(self, person_count):
        self.history.append(person_count)
    
    def establish_baseline(self, first_n_frames=30):
        if len(self.history) >= first_n_frames:
            self.baseline = sum(self.history[:first_n_frames]) / first_n_frames
            self.peak = max(self.history)
            return True
        return False
    
    def get_pattern(self, current_count):
        if self.baseline is None:
            return None
        
        deviation = ((current_count - self.baseline) / self.baseline) * 100
        
        return {
            "avg_people": self.baseline,
            "peak_people": self.peak,
            "current_people": current_count,
            "deviation_percent": deviation,
            "baseline_source": "first 30 frames of video"
        }