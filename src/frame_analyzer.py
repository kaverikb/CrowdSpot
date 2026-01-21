import cv2
from ultralytics import YOLO
import numpy as np


class FrameAnalyzer:
    def __init__(self, model_name="yolov8l.pt"):
        self.model = YOLO(model_name)
        self.person_class = 0
    
    def detect_frame(self, frame):
        results = self.model(frame, verbose=False, conf=0.1)
        return results[0]
    
    def extract_persons(self, detection_result):
        persons = []
        for box in detection_result.boxes:
            if int(box.cls[0]) == self.person_class:
                persons.append(box)
        return persons
    
    def get_centroids(self, persons):
        centroids = []
        confidences = []
        bboxes = []
        
        for person in persons:
            x1, y1, x2, y2 = person.xyxy[0].cpu().numpy()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            conf = float(person.conf[0])
            
            centroids.append((cx, cy))
            confidences.append(conf)
            bboxes.append((int(x1), int(y1), int(x2), int(y2)))
        
        return centroids, confidences, bboxes
    
    def analyze_frame(self, frame, frame_idx=0, timestamp=0.0):
        if frame is None:
            return None
        
        h, w = frame.shape[:2]
        
        detection_result = self.detect_frame(frame)
        persons = self.extract_persons(detection_result)
        centroids, confidences, bboxes = self.get_centroids(persons)
        
        person_count = len(persons)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'frame_idx': frame_idx,
            'timestamp': timestamp,
            'person_count': person_count,
            'centroids': centroids,
            'confidences': confidences,
            'bboxes': bboxes,
            'avg_confidence': avg_confidence,
            'frame_shape': (h, w),
            'raw_detections': persons
        }