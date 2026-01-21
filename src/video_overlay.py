import cv2
import numpy as np


class VideoOverlay:

    def __init__(self, frame_shape):
        self.h, self.w = frame_shape[:2]

    def draw_bounding_boxes(self, frame, bboxes, color=(0, 255, 0), thickness=2):
        for x1, y1, x2, y2 in bboxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        return frame

    def draw_centroids(self, frame, centroids, color=(0, 255, 255), radius=5):
        for cx, cy in centroids:
            cv2.circle(frame, (int(cx), int(cy)), radius, color, -1)
        return frame

    def draw_density_heatmap(self, frame, centroids, grid_size=100, alpha=0.3):
        if not centroids:
            return frame

        heatmap = np.zeros((self.h, self.w), dtype=np.float32)

        for cx, cy in centroids:
            cv2.circle(heatmap, (int(cx), int(cy)), grid_size // 2, 1.0, -1)

        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        result = cv2.addWeighted(frame, 1 - alpha, heatmap_color, alpha, 0)
        return result

    def draw_count_text(self, frame, count, pos=(10, 30), font_scale=1.0, color=(0, 255, 0)):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Count: {count}", pos, font, font_scale, color, 2)
        return frame

    def draw_timestamp(self, frame, timestamp, pos=None, font_scale=0.7, color=(0, 255, 0)):
        if pos is None:
            pos = (10, self.h - 10)

        cv2.putText(frame, f"Time: {timestamp:.2f}s", pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1)
        return frame

    def annotate_frame(self, frame, detection, is_alert=False):
        frame_copy = frame.copy()

        frame_copy = self.draw_density_heatmap(frame_copy, detection['centroids'])
        frame_copy = self.draw_bounding_boxes(frame_copy, detection['bboxes'])
        frame_copy = self.draw_centroids(frame_copy, detection['centroids'])
        frame_copy = self.draw_count_text(frame_copy, detection['person_count'])
        frame_copy = self.draw_timestamp(frame_copy, detection['timestamp'])

        if is_alert:
            h, w = frame_copy.shape[:2]
            cv2.rectangle(frame_copy, (0, 0), (w, 60), (0, 0, 255), -1)
            cv2.putText(frame_copy, "ALERT DETECTED", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        return frame_copy