import cv2
import time
import os
import pandas as pd
from ultralytics import YOLO

# Define variables
detected_offset = 8
line_position = 395
frame_rate = 24  # Adjust if needed based on your video frame rate
min_detections_for_fit = 30

# Load the trained YOLO model
model = YOLO(r"D:\Management\Personal\Reva AI\CP\Fastner detection\New\YoloUI\detect\train11\weights\best.pt") 

def process_video(video_path):
  """
  Processes a video, counts detected objects crossing a line, and determines fitness.

  Args:
    video_path: Path to the video file.

  Returns:
    A tuple containing:
      - count: Number of detected objects crossing the line.
      - fitness: "FitToRunTrain" or "NotFitToRunTrain".
  """
  cap = cv2.VideoCapture(video_path)
  if not cap.isOpened():
    print(f"Error: Could not open video '{video_path}'.")
    return None, None

  frame_count = 0
  count = 0
  detected = []

  while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
      break

    # Perform object detection using YOLO
    results = model(frame)
    frame_width = frame.shape[1]

    # Draw a horizontal line across the frame (optional for visualization)
    cv2.line(frame, (0, line_position), (frame_width, line_position), (255, 127, 0), 3)

    # Process detections
    for result in results:
      for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = box.conf[0]
        class_id = box.cls[0]

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw bounding box and center point (optional for visualization)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
        cv2.putText(frame, f"ID: {int(class_id)} Conf: {confidence:.2f}",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        detected.append((cx, cy))

    # Object counting logic
    for (x, y) in detected:
      if y in range(line_position - detected_offset, line_position + detected_offset + 1) and x in range(10, 200):
        count += 1
        detected.remove((x, y))

    # Show the frame (optional for visualization)
    cv2.imshow('Object Detection', frame)
    if cv2.waitKey(1) & 0xFF == 27:
      break

    # Simulate video playback speed
    time.sleep(1 / frame_rate)

  cap.release()
  cv2.destroyAllWindows()

  # Determine fitness based on the count
  fitness = "FitToRunTrain" if count > min_detections_for_fit else "NotFitToRunTrain"
  return count, fitness

# # Get video path from user input
# video_path = input("Enter the path to the video file: ")

# # Process the video and get results
# count, fitness = process_video(video_path)

# # Print the results
# if count is not None:
#   print(f"RailTiePlates Detected: {count}")
#   print(f"Track Fitness: {fitness}")
# else:
#   print("Video processing failed.")