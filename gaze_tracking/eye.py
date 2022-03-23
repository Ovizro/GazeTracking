import math
import numpy as np
import cv2
from typing import Any, List, Tuple

from .pupil import Pupil
from .calibration import Calibration


LEFT_EYE = 0
RIGHT_EYE = 1


def _middle_point(p1: np.ndarray, p2: np.ndarray) -> Tuple[int, int]:
    """Returns the middle point (x,y) between two points

    Arguments:
        p1 (np.ndarray): First point
        p2 (np.ndarray): Second point
    """
    return tuple((p1 + p2) // 2)


class Eye(object):
    """
    This class creates a new frame to isolate the eye and
    initiates the pupil detection.
    """
    __slots__ = ["pupil", "landmark_points", "frame", "origin", "center", "blinking"]

    LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47]

    def __init__(self, original_frame: np.ndarray, landmarks: Any, side: int, calibration: Calibration):
        """Detects and isolates the eye in a new frame, sends data to the calibration
        and initializes Pupil object.

        Arguments:
            original_frame (numpy.ndarray): Frame passed by the user
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            side: Indicates whether it's the left eye (0) or the right eye (1)
            calibration (calibration.Calibration): Manages the binarization threshold value
        """
        if side == LEFT_EYE:
            points = self.LEFT_EYE_POINTS
        elif side == RIGHT_EYE:
            points = self.RIGHT_EYE_POINTS
        else:
            return

        region: np.ndarray = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points])
        region = region.astype(np.int32)
        self.landmark_points = region
        
        self.blinking = self._blinking_ratio(landmarks, points)
        self._isolate(original_frame, landmarks, points)

        if not calibration.is_complete():
            calibration.evaluate(self.frame, side)

        threshold = calibration.threshold(side)
        self.pupil: Pupil = Pupil(self.frame, threshold)

    def _isolate(self, frame: np.ndarray, landmarks: Any, points: List[int]) -> None:
        """Isolate an eye, to have a frame without other part of the face.

        Arguments:
            frame (numpy.ndarray): Frame containing the face
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)
        """
        # Applying a mask to get only the eye
        height, width = frame.shape[:2]
        black_frame = np.zeros((height, width), np.uint8)
        mask = np.full((height, width), 255, np.uint8)
        cv2.fillPoly(mask, [self.landmark_points], (0, 0, 0))
        eye: np.ndarray = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)

        # Cropping on the eye
        margin = 5
        min_x = np.min(self.landmark_points[:, 0]) - margin
        max_x = np.max(self.landmark_points[:, 0]) + margin
        min_y = np.min(self.landmark_points[:, 1]) - margin
        max_y = np.max(self.landmark_points[:, 1]) + margin

        self.frame: np.ndarray = eye[min_y:max_y, min_x:max_x]
        self.origin: Tuple[int, int] = (min_x, min_y)
        
        height, width = self.frame.shape[:2]
        self.center = (width / 2, height / 2)

    @property
    def left(self) -> Tuple[int, int]:
        return self.landmark_points[0]
    
    @property
    def right(self) -> Tuple[int, int]:
        return self.landmark_points[3]
    
    @property
    def top(self) -> Tuple[int, int]:
        return _middle_point(self.landmark_points[1], self.landmark_points[2])
        
    @property
    def bottom(self) -> Tuple[int, int]:
        return _middle_point(self.landmark_points[4], self.landmark_points[5])

    def _blinking_ratio(self, landmarks, points: List[int]) -> float:
        """Calculates a ratio that can indicate whether an eye is closed or not.
        It's the division of the width of the eye, by its height.

        Arguments:
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)

        Returns:
            The computed ratio
        """
        left = self.left
        right = self.right
        top = self.top
        bottom = self.bottom

        eye_width = math.hypot((left[0] - right[0]), (left[1] - right[1]))
        eye_height = math.hypot((top[0] - bottom[0]), (top[1] - bottom[1]))

        try:
            ratio = eye_width / eye_height
        except ZeroDivisionError:
            ratio = 0

        return ratio