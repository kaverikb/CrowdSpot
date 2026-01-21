import cv2

video_path = r"C:\Users\Kaveri\Downloads\test_video.mp4"

cap = cv2.VideoCapture(video_path)

if cap.isOpened():
    print("Video loaded successfully!")
    print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    print(f"Frame count: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
    print(f"Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    cap.release()
else:
    print("Failed to load video")