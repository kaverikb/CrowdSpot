from src.video_processor import VideoProcessor


def main():
    video_path = r"C:\Users\Kaveri\Downloads\test_video.mp4"
    location = "Shibuya Crossing"
    
    processor = VideoProcessor(video_path, output_dir="results")
    output_video, alerts_log = processor.process_video(location=location)


if __name__ == "__main__":
    main()