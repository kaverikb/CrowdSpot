import cv2
import json
from pathlib import Path
from datetime import datetime

from src.rag_integration import RAGIntegration
from src.video_overlay import VideoOverlay
from src.video_tracker import CentroidTracker


class VideoProcessor:
    def __init__(self, video_path, output_dir="results"):
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.cap = cv2.VideoCapture(str(self.video_path))
        
        if not self.cap.isOpened():
            raise FileNotFoundError(f"Cannot open: {self.video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video: {self.video_path}")
        print(f"FPS: {self.fps}, Frames: {self.frame_count}, Size: {self.width}x{self.height}")
        
        self.rag = RAGIntegration()
        self.overlay = VideoOverlay((self.height, self.width))
        self.tracker = CentroidTracker(max_distance=50)
        
        self.baseline = None
        self.peak = None
        self.alerts = []
    
    def process_video(self, location="Shibuya Crossing"):
        output_video_path = self.output_dir / "video_output.avi"
        alerts_path = self.output_dir / "alerts_timeline.json"
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(
            str(output_video_path),
            fourcc,
            self.fps,
            (self.width, self.height)
        )
        
        frame_idx = 0
        baseline_set = False
        
        print("Processing frames...")
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            timestamp = frame_idx / self.fps
            
            try:
                result = self.rag.process_frame(frame, location, timestamp)
            except Exception as e:
                print(f"Error processing frame {frame_idx}: {e}")
                frame_idx += 1
                continue
            
            if result is None:
                frame_idx += 1
                continue
            
            # Establish baseline on first 30 frames
            if not baseline_set and len(self.rag.baseline.history) >= 30:
                self.rag.baseline.establish_baseline(first_n_frames=30)
                baseline_set = True
                
                self.baseline = self.rag.baseline.baseline
                self.peak = self.rag.baseline.peak
                print(f"Baseline: {self.baseline:.0f} | Peak: {self.peak}")
            
            person_count = result['detection']['person_count']
            
            # Alert if count reaches peak
            is_alert = False
            if baseline_set and person_count >= self.peak:
                is_alert = True
                alert = {
                    'timestamp': timestamp,
                    'frame': frame_idx,
                    'count': person_count,
                    'llm': result['llm'],
                    'pattern': result['pattern']
                }
                self.alerts.append(alert)
                print(f"ALERT at {timestamp:.1f}s: {person_count} people")
            
            # Annotate frame
            try:
                result['detection']['timestamp'] = timestamp
                annotated = self.overlay.annotate_frame(
                    frame,
                    result['detection'],
                    is_alert=is_alert
                )
            except Exception as e:
                print(f"Error annotating frame {frame_idx}: {e}")
                annotated = frame
            
            out.write(annotated)
            
            if (frame_idx + 1) % 30 == 0:
                progress = (frame_idx + 1) / self.frame_count * 100
                print(f"  {frame_idx + 1}/{self.frame_count} ({progress:.0f}%)")
            
            frame_idx += 1
        
        self.cap.release()
        out.release()
        
        print("Done!")
        print(f"Video: {output_video_path}")
        print(f"Total alerts: {len(self.alerts)}")
        
        with open(alerts_path, 'w') as f:
            json.dump({
                'baseline': self.baseline,
                'peak': self.peak,
                'alerts': self.alerts,
                'processed': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"Alerts: {alerts_path}")
        
        return str(output_video_path), str(alerts_path)