import csv
import numpy as np
from pathlib import Path

from detector import PersonDetector, load_all_images
from density import DensityEstimator
from anomaly import AnomalyDetector
from alert import AlertGenerator


class Pipeline:
    def __init__(self):
        self.detector = PersonDetector("yolov8n.pt")
        self.density = DensityEstimator()
        self.anomaly = AnomalyDetector(k=2)
        self.alert_gen = AlertGenerator()

        self.results_frames = []
        self.results_anomalies = []
        self.results_alerts = []

        self.all_densities = []
        self.baseline_mean = None
        self.baseline_std = None

    def process_all(self):
        images = load_all_images()
        print(f"Processing {len(images)} images...")

        #detecction & density
        for idx, img_path in enumerate(images):
            if idx % 50 == 0:
                print(f"Processing {idx}/{len(images)}")

            det_result = self.detector.process_image(img_path)
            if det_result is None:
                continue

            global_density = self.density.global_density(
                det_result["person_count"],
                det_result["image_shape"]
            )

            self.all_densities.append(global_density)

            frame_row = {
                "image_id": str(img_path.relative_to("data/videos")),
                "timestamp": idx,
                "person_count": det_result["person_count"],
                "global_density": global_density,
                "confidence": (
                    sum(det_result["confidences"]) /
                    max(len(det_result["confidences"]), 1)
                ),
            }

            self.results_frames.append(frame_row)

        if not self.results_frames:
            raise RuntimeError("No frames processed. Check dataset or detector.")

        
        self.calculate_baseline()

        #Buckets analomalies and alerts
        for frame in self.results_frames:
            # 🔹 CORRECT: bucket from stored global_density
            frame["density_level"] = self.density.density_bucket(
                frame["global_density"],
                self.baseline_mean,
                self.baseline_std
            )

            anom_result = self.anomaly.detect(
    density=frame["global_density"],
    mean=self.baseline_mean,
    std=self.baseline_std,
    hot_cells=0,
    expected_hot_cells=1,
    confidence=frame["confidence"]
)


            self.results_anomalies.append({
                "image_id": frame["image_id"],
                "person_count": frame["person_count"],
                "global_density": frame["global_density"],
                "z_score": anom_result["z_score"],
                "severity": anom_result["severity"],
                "anomaly_type": (
                    "ATYPICAL" if anom_result["is_anomaly"] else "NORMAL"
                ),
            })

            if self.alert_gen.should_alert(anom_result["severity"]):
                alert = self.alert_gen.create_alert(
                    anom_result,
                    zone=frame["image_id"],
                    person_count=frame["person_count"],
                    baseline_density=self.baseline_mean
                )
                self.results_alerts.append(alert)

    def calculate_baseline(self):
        self.baseline_mean = float(np.mean(self.all_densities))
        self.baseline_std = float(np.std(self.all_densities))

        with open("data/baselines.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerow(["baseline_mean", self.baseline_mean])
            writer.writerow(["baseline_std", self.baseline_std])

    def save_results(self):
        self.save_frames()
        self.save_anomalies()
        self.save_alerts()

    def save_frames(self):
        with open("results/frames.csv", "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=self.results_frames[0].keys()
            )
            writer.writeheader()
            writer.writerows(self.results_frames)

    def save_anomalies(self):
        with open("results/anomalies.csv", "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=self.results_anomalies[0].keys()
            )
            writer.writeheader()
            writer.writerows(self.results_anomalies)

    def save_alerts(self):
        if not self.results_alerts:
            return

        with open("results/alerts.csv", "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=self.results_alerts[0].keys()
            )
            writer.writeheader()

            for alert in self.results_alerts:
                alert["timestamp"] = str(alert["timestamp"])
                alert["expiry"] = str(alert["expiry"])

            writer.writerows(self.results_alerts)


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.process_all()
    pipeline.save_results()
    print("Done! Results saved to results/")
