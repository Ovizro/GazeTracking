"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""


import cv2
import numpy as np
from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not webcam.grab():
    exit()

count = r_count = h_count = 0


while True:
    # We get a new frame from the webcam
    raw_frame: np.ndarray
    frame: np.ndarray

    _, raw_frame = webcam.read()
    raw_frame = cv2.flip(raw_frame, 1)

    # We send this frame to GazeTracking to analyze it
    count += 1

    gaze.equalizehist = False
    gaze.refresh(raw_frame)
    if gaze.pupils_located:
        r_count += 1
    raw_frame_ret: np.ndarray = gaze.annotated_frame()

    gaze.equalizehist = True
    gaze.refresh(raw_frame)
    if gaze.pupils_located:
        h_count += 1
    frame: np.ndarray = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"
    else:
        ...

    pic = np.hstack((raw_frame_ret, frame))
    cv2.imwrite("output.png", pic)


    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    cv2.putText(
        frame,
        f"Left pupil:  {str(left_pupil)}",
        (90, 130),
        cv2.FONT_HERSHEY_DUPLEX,
        0.9,
        (147, 58, 31),
        1,
    )

    cv2.putText(
        frame,
        f"Right pupil: {str(right_pupil)}",
        (90, 165),
        cv2.FONT_HERSHEY_DUPLEX,
        0.9,
        (147, 58, 31),
        1,
    )


    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) == 27:
        break

webcam.release()
cv2.destroyAllWindows()
print(f"Total count: {count}\n", r_count / count, h_count / count)