import numpy as np
from scipy.ndimage import gaussian_filter


class DensityEstimator:
    def __init__(self, grid_size=5):
        self.grid_size = grid_size

    def global_density(self, person_count, image_shape):
        h, w = image_shape
        area = h * w
        return person_count / area

    def density_bucket(self, density, mean, std):
     if density < mean - 0.25 * std:
        return "LOW"
     elif density < mean + 1.25 * std:
        return "MEDIUM"
     else:
        return "HIGH"



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
        max_local_density = float(np.max(grid))
        return hot_count, max_local_density

    def process(self, person_count, centroids, image_shape, baseline_mean, baseline_std):
        global_density = self.global_density(person_count, image_shape)
        density_level = self.density_bucket(
            global_density,
            baseline_mean,
            baseline_std
        )

        spatial_map = self.spatial_map(centroids, image_shape)
        hot_cells, max_local_density = self.hot_cells(spatial_map)

        return {
            "global_density": global_density,
            "density_level": density_level,
            "spatial_map": spatial_map,
            "hot_cells": hot_cells,
            "max_local_density": max_local_density
        }
