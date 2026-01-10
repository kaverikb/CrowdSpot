import numpy as np


class AnomalyDetector:
    def __init__(self, k=2):
        self.k = k
    
    def calc_baseline(self, densities):
        mean = np.mean(densities)
        std = np.std(densities)
        return mean, std
    
    def z_score(self, value, mean, std):
        if std == 0:
            return 0
        return (value - mean) / std
    
    def get_severity(self, z_score, hot_cells_ratio=None):
        if abs(z_score) < 1.5:
            return "LOW"
        elif abs(z_score) < 2:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def detect(self, density, mean, std, hot_cells, expected_hot_cells, confidence):
        z = self.z_score(density, mean, std)
        
        threshold = mean + (self.k * std)
        is_anomaly = density > threshold
        
        hot_ratio = hot_cells / max(expected_hot_cells, 1)
        
        severity = self.get_severity(z, hot_ratio)
        
        if confidence < 0.6:
            severity = "LOW"
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': z,
            'severity': severity,
            'threshold': threshold
        }