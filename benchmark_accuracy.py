import cv2
import json
import time
import numpy as np
import os 

def convert_output_to_json(output_array):
    json_output = []
    for item in output_array:
        min_x, min_y, max_x, max_y, car_id, car_type, _ = item

        # Assuming the conversion for x and y coordinates as per the given example
        # It's not clear how to convert these values, so I'm assuming a linear transformation based on the example given
        # This part might need adjustment based on the actual transformation rules you have
        min_x = min_x 
        min_y = min_y 
        max_x = max_x
        max_y = max_y 

        json_entry = {
            "car_id": str(car_id),  
            "type": int(car_type),
            "min_x": min_x,
            "min_y": min_y,
            "max_x": max_x,
            "max_y": max_y
        }
        json_output.append(json_entry)

    # Convert to JSON string
    json_string = json.dumps(json_output, indent=4)
    return json_string

def show_frames(label_json_file, video_path):
    # Load JSON data
    with open(label_json_file, 'r') as file:
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
                scale_x, scale_y = new_width / frame_width * 38.4, new_height / frame_height * 21.6

                min_x, min_y, max_x, max_y = int(obj['min_x'] * scale_x), int(obj['min_y'] * scale_y), \
                                            int(obj['max_x'] * scale_x), int(obj['max_y'] * scale_y)
                car_id = obj['car_id']

                # Draw rectangle and text
                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                cv2.putText(frame, car_id, (min_x, min_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                #cv2.rectangle(frame, (int(697 * new_width / frame_width), int(1830 * new_height / frame_height)), (int(1510 * new_width / frame_width), int(2160 * new_height / frame_height)), (0, 255, 0), 2)        
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

def saveImage(image, path, i):
    if not os.path.exists(path):
        os.makedirs(path)
    filename = f"frame_{i}.jpg"
    cv2.imwrite(os.path.join(path, filename), image)

def save_frame(video_path, frame_number, labels, trackings, matches, saved_matchings):
    # Capture video
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Set the frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frame
    ret, frame = cap.read()

    # Resize frame
    frame_height, frame_width = frame.shape[:2]

    new_width = 1200
    aspect_ratio = frame_height / frame_width
    new_height = int(new_width * aspect_ratio)
    frame = cv2.resize(frame, (new_width, new_height))

    if not ret:
        print("Error: Could not read frame.")
        cap.release()
        return

    scale_x, scale_y = new_width / frame_width, new_height / frame_height

    matched_ids = []
    for elem in matches:
        matched_ids.append(elem[0])
        matched_ids.append(elem[1])

    for bbox in labels:
        x1, y1, x2, y2, id = bbox
        color = (0,0,0)
        """
        if id in matched_ids:
            color = (57,255,20)
        else:
            color = (0, 0, 255)
        """
        if id in saved_matchings:
            if saved_matchings[id][1] == "true_id":
                if saved_matchings[id][2] == "in_frame":
                   color = (57,255,20)
                else: 
                    color = (255,105,0)
            
            elif saved_matchings[id][1] == "switched_id":
                color = (0, 0, 255)
            

        cv2.rectangle(frame, (int(x1 * scale_x), int(y1 * scale_y)), (int(x2 * scale_x), int(y2 * scale_y)), color, 2)

    """
    # Draw trackings in blue
    for bbox in trackings:
        x1, y1, x2, y2, id = bbox
        if id in matched_ids:
            color = (57,255,20)
        else:
            color = (0, 0, 255)
    """

        #cv2.rectangle(frame, (int(x1 * scale_x), int(y1 * scale_y)), (int(x2 * scale_x), int(y2 * scale_y)), color, 2)

    # Display the frame
    saveImage(frame, "benchmarks/accuracy/bytetrack/frames_annotated/", frame_number)
    #cv2.imwrite(f"benchmarks/accuracy/bytetrack/{frame_number}", frame)

    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Release video capture
    cap.release()



def get_true_labels(frame_num, label_json_file):
    # Load labels from JSON
    with open(label_json_file, 'r') as file:
        json_labels = json.load(file)
    
    # get labels from current frame
    current_labels = json_labels[str(frame_num)]

    # prepare output
    current_formatted_labels = []

    # extract data, format coordinates because label studio format is in percent of video width/height, we need pixels
    for elem in current_labels:
        current_formatted_labels.append([elem["min_x"] * 38.4, elem["min_y"] * 21.6, elem["max_x"] * 38.4, elem["max_y"] * 21.6, elem["car_id"],])

    return current_formatted_labels


def format_tracks(current_trackings):
    tracks = []

    for elem in current_trackings:
        min_x = elem[0]
        min_y = elem[1]
        max_x = elem[2]
        max_y = elem[3]
        car_id = elem[4]
        tracks.append([min_x, min_y, max_x, max_y, car_id])

    return tracks

def calculate_iou(bbox1, bbox2):
    x1, y1, x2, y2 = bbox1
    x1_p, y1_p, x2_p, y2_p = bbox2

    # Calculate the (x, y)-coordinates of the intersection rectangle
    xA = max(x1, x1_p)
    yA = max(y1, y1_p)
    xB = min(x2, x2_p)
    yB = min(y2, y2_p)

    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # Compute the area of both bboxes
    bbox1Area = (x2 - x1) * (y2 - y1)
    bbox2Area = (x2_p - x1_p) * (y2_p - y1_p)

    # Compute the intersection over union
    iou = interArea / float(bbox1Area + bbox2Area - interArea)

    return iou

def alignment_focused_iou(boxA, boxB):
    # Calculate the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # Compute the area of both bounding boxes
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    # Compute the area of the smaller box
    smallerBoxArea = min(boxAArea, boxBArea)

    #print(smallerBoxArea)

    # Compute the alignment focused IoU score
    score = interArea / float(smallerBoxArea)

    return score


def map_bboxes(trackings, labels, iou_threshold=0.3):
    matched_pairs = []
    matched_ids = set()

    for bbox1 in trackings:
        id1, coords1 = bbox1[-1], bbox1[:-1]
        best_match = (-1, 0)  

        # TODO sometimes there are trackings with only zero values, hotfix for now
        if sum(coords1) == 0:
            continue

        for bbox2 in labels:
            id2, coords2 = bbox2[-1], bbox2[:-1]

            # TODO
            if sum(coords2) == 0:
                continue

            iou = alignment_focused_iou(coords1, coords2)

            # Check if this is the best match so far and IoU exceeds the threshold
            if iou > best_match[1] and iou >= iou_threshold:
                best_match = (id2, iou)

        # Add the best match to the output, or a no-match indicator if none found
        if best_match[0] != -1:
            matched_pairs.append((id1, best_match[0]))
            matched_ids.add(best_match[0])
        else:
            matched_pairs.append((-1, id1))

    # Add unmatched bboxes from the second array
    for bbox2 in labels:
        if bbox2[-1] not in matched_ids:
            matched_pairs.append((-1, bbox2[-1]))

    return matched_pairs

def update_saved_matches(saved_matchings, matches):
    counter = saved_matchings["counter"]

    for elem in matches:
        # new true object, create new entry in saved_matchings
        if elem[1] not in saved_matchings:
            saved_matchings[elem[1]] = [-1, "no_id", "not_in_frame"]
        
        # true object is already there 
        if elem[1] in saved_matchings:
            # tracker has not found yet
            if elem[0] == -1 and saved_matchings[elem[1]][0] == -1:
                continue

            # tracker has already found, object in current frame missing
            elif saved_matchings[elem[1]][1] == "true_id" and elem[0] == -1:
                saved_matchings[elem[1]][2] = "not_in_frame"
                counter["lost_frames"] += 1
                

            # id already switched
            elif saved_matchings[elem[1]][1] == "switched_id":
                continue

            # tracker finds first time
            elif elem[0] != -1 and saved_matchings[elem[1]][0] == -1:
                saved_matchings[elem[1]] = [elem[0], "true_id", "in_frame"]

            # tracker has already found
            elif elem[0] != -1 and saved_matchings[elem[1]][0] != -1:
                # car id is the same 
                if saved_matchings[elem[1]][0] == elem[0]:
                    saved_matchings[elem[1]][1] = "true_id"
                    saved_matchings[elem[1]][2] = "in_frame"
                # car id switch
                else:
                    saved_matchings[elem[1]][1] = "switched_id"
                    saved_matchings[elem[1]][2] = "in_frame"
                    counter["id_switches"] += 1
    
    saved_matchings["counter"] = counter
            
    return saved_matchings



def accuracy(current_trackings, saved_matchings, frame_num, label_json_file, video_path, save=False):

    current_trackings = format_tracks(current_trackings)
    current_labels = get_true_labels(frame_num, label_json_file)

    matches = map_bboxes(current_trackings, current_labels)

    saved_matchings = update_saved_matches(saved_matchings, matches)

    # TODO cleanup
    if save:
        save_frame(video_path, frame_num, current_labels, current_trackings, matches, saved_matchings)
    
    return saved_matchings

