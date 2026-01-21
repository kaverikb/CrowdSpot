import numpy as np
from scipy.ndimage import gaussian_filter


class DensityAnalyzer:
    def __init__(self, grid_size=5):
        self.grid_size = grid_size
        self.history = []
    
    def analyze(self, person_count):
        self.history.append(person_count)
        
        if len(self.history) < 3:
            return "low"
        
        avg = sum(self.history[-10:]) / len(self.history[-10:])
        
        if person_count > avg * 1.5:
            return "high"
        elif person_count > avg * 1.2:
            return "medium"
        else:
            return "low"
    
    def calculate_z_score(self, person_count):
        if len(self.history) < 2:
            return 0
        
        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        std = variance ** 0.5
        
        if std == 0:
            return 0
        
        return (person_count - mean) / std
    
    def global_density(self, person_count, image_shape):
        h, w = image_shape
        area = h * w
        return person_count / area
    
    def spatial_map(self, centroids, image_shape):
        h, w = image_shape
        grid = np.zeros((self.grid_size, self.grid_size))
        
        for cx, cy in centroids:
            x = int((cx / w) * self.grid_size)
            y = int((cy / h) * self.grid_size)
            
            x = min(max(x, 0), self.grid_size - 1)
            y = min(max(y, 0), self.grid_size - 1)
            
            grid[y, x] += 1
        
        return gaussian_filter(grid, sigma=0.5)
    
    def hot_cells(self, grid, threshold=0.5):
        hot_count = int(np.sum(grid > threshold))
        max_density = float(np.max(grid))
        return hot_count, max_density
    
    def process(self, person_count, centroids, image_shape):
        global_dens = self.global_density(person_count, image_shape)
        density_level = self.analyze(person_count)
        
        spatial = self.spatial_map(centroids, image_shape)
        hot_count, max_dens = self.hot_cells(spatial)
        
        return {
            "global_density": global_dens,
            "density_level": density_level,
            "spatial_map": spatial,
            "hot_cells": hot_count,
            "max_local_density": max_dens
        }