import math

class CentroidTracker:
    
    def __init__(self, max_distance=50):
    
        self.max_distance = max_distance
        self.tracked_objects = {}
        self.next_id = 1
    
    def distance(self, pt1, pt2):
        #euclidean dist
        return math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
    
    def track(self, centroids):
    
        if len(centroids) == 0:
            # No detections, mark existing as lost
            self.tracked_objects = {}
            return {}
        
        # If no previous tracks, assign new IDs
        if len(self.tracked_objects) == 0:
            for centroid in centroids:
                self.tracked_objects[self.next_id] = centroid
                self.next_id += 1
            return self.tracked_objects.copy()
        
        # Match centroids to previous tracks
        updated_tracks = {}
        used_detections = set()
        
        for track_id, prev_centroid in self.tracked_objects.items():
            best_match = None
            best_distance = self.max_distance
            best_idx = -1
            
            # Find closest centroid
            for i, centroid in enumerate(centroids):
                if i in used_detections:
                    continue
                
                d = self.distance(prev_centroid, centroid)
                
                if d < best_distance:
                    best_distance = d
                    best_match = centroid
                    best_idx = i
            
            # Update track if match found
            if best_match is not None:
                updated_tracks[track_id] = best_match
                used_detections.add(best_idx)
        
        # Assign new IDs to unmatched detections
        for i, centroid in enumerate(centroids):
            if i not in used_detections:
                updated_tracks[self.next_id] = centroid
                self.next_id += 1
        
        self.tracked_objects = updated_tracks
        return updated_tracks.copy()