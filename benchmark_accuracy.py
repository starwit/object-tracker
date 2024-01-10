import cv2
import json
import time

label_json = "benchmarks/accuracy/frame_labels.json"
video_path = "benchmarks/accuracy/CAM-HAZELDELL-126THST_25fps.mp4"

# Load JSON data
with open(label_json, 'r') as file:
    bounding_boxes = json.load(file)

# Open the video file
video = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not video.isOpened():
    print("Error: Could not open video.")
    exit()


# Frame counter and skip frame flag
frame_number = 0
skip_frame = 0

while video.isOpened():
    ret, frame = video.read()
    if not ret:
        break

    
    # Increase frame counter
    frame_number += 1

    # Skip every 6th frame to simulate 25 fps from 30 fps
    if skip_frame == 5:
        skip_frame = 0
        continue
    skip_frame += 1


    # Resize frame
    frame_height, frame_width = frame.shape[:2]
    new_width = 1200
    aspect_ratio = frame_height / frame_width
    new_height = int(new_width * aspect_ratio)
    frame = cv2.resize(frame, (new_width, new_height))

    # Fetch bounding box data for the current frame
    if str(frame_number) in bounding_boxes:
        for obj in bounding_boxes[str(frame_number)]:
            # Extract bounding box coordinates and scale them according to the new frame size
            # scaling in a very very dirty way because the values are weird and i didn't had the time to do this the right way yet
            scale_x, scale_y = new_width / frame_width * 38.5, new_height / frame_height * 21.5

            min_x, min_y, max_x, max_y = int(obj['min_x'] * scale_x), int(obj['min_y'] * scale_y), \
                                          int(obj['max_x'] * scale_x), int(obj['max_y'] * scale_y)
            car_id = obj['car_id']

            # Draw rectangle and text
            cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
            cv2.putText(frame, car_id, (min_x, min_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.rectangle(frame, (int(697 * new_width / frame_width), int(1830 * new_height / frame_height)), (int(1510 * new_width / frame_width), int(2160 * new_height / frame_height)), (0, 255, 0), 2)        
            if car_id == "pr_spml2LR":
                print(frame_number, obj['min_x'], obj['min_y'], obj['max_x'], obj['max_y'])
        #if frame_number > 400:
            #time.sleep(0.5)
        #if frame_number == 425:
            #break

    # Display the frame
    cv2.imshow('Frame', frame)

    # Press 'q' to exit the video window
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    #frame_number += 1

# Release the video capture object
video.release()
cv2.destroyAllWindows()