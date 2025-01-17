import cv2
from gaze_tracking import GazeTrackingFromVideo

gaze = GazeTrackingFromVideo(1, flip=True)


for _ in gaze:
    frame = gaze.annotated_frame()
    
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    if gaze.pupils_located:
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