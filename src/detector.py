import cv2
from ultralytics import YOLO
from pathlib import Path


class PersonDetector:
    def __init__(self, model_name="yolov8n.pt"):
        self.model = YOLO(model_name)
        self.person_class = 0
    
    def detect(self, image):
        results = self.model(image, verbose=False)
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
        
        for person in persons:
            x1, y1, x2, y2 = person.xyxy[0].cpu().numpy()
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            conf = float(person.conf[0])
            
            centroids.append((cx, cy))
            confidences.append(conf)
        
        return centroids, confidences
    
    def process_image(self, image_path):
        image = cv2.imread(str(image_path))
        
        if image is None:
            return None
        
        h, w = image.shape[:2]
        results = self.detect(image)
        persons = self.extract_persons(results)
        centroids, confidences = self.get_centroids(persons)
        
        return {
            'person_count': len(persons),
            'centroids': centroids,
            'confidences': confidences,
            'image_shape': (h, w),
            'image_path': image_path
        }



def load_all_images():
    base_dir = Path("data/videos")
    image_paths = []

    for part in ["part_A", "part_B"]:
        for split in ["train_data", "test_data"]:
            img_dir = base_dir / part / split / "images"
            if img_dir.exists():
                image_paths.extend(img_dir.glob("*.jpg"))

    return sorted(image_paths)



if __name__ == "__main__":
    detector = PersonDetector("yolov8n.pt")
    images = load_all_images()
    
    if images:
        test_image = images[0]
        print(f"Testing: {test_image}")
        
        result = detector.process_image(test_image)
        
        if result:
            print(f"Persons: {result['person_count']}")
            print(f"Shape: {result['image_shape']}")
            print(f"Centroids: {result['centroids'][:3]}")
            print(f"Confidence: {result['confidences'][:3]}")
    else:
        print("No images found")