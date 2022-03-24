from __future__ import division
import os
from typing import Union
import numpy as np
import cv2
import dlib
from .eye import BOTH_EYES, LEFT_EYE, RIGHT_EYE, Eye
from .calibration import Calibration


def hisEqulColor(img: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    channels = cv2.split(ycrcb)
    # print len(channels)
    cv2.equalizeHist(channels[0], channels[0])
    cv2.merge(channels, ycrcb)
    cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR, img)
    return img


class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    __slots__ = ["frame", "eye_left", "eye_right", "calibration",
                "equalizehist", "_face_detector", "_predictor"]

    def __init__(self, frame: Union[np.ndarray, str, None] = None, *, equalizehist: bool = False):
        self.equalizehist = int(equalizehist)
        self.calibration = Calibration()

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)
        
        if frame is not None:
            if isinstance(frame, str):
                frame = cv2.imread(frame)
            self.refresh(frame)

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        if self.eye_left is None or self.eye_right is None:
            return False

        return all(i > 0 for i in [
            self.eye_left.pupil.x, self.eye_left.pupil.y, self.eye_right.pupil.x, self.eye_right.pupil.y])

    def _analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        if self.equalizehist == 1:
            frame = cv2.equalizeHist(frame)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame: np.ndarray):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        if self.equalizehist == 2:
            self.equalizehist = 1
        self._analyze()

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        horizontal direction of the gaze. The extreme right is 0.0,
        the center is 0.5 and the extreme left is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def is_right(self):
        """Returns true if the user is looking to the right"""
        if self.pupils_located:
            return self.horizontal_ratio() <= 0.35

    def is_left(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.horizontal_ratio() >= 0.65

    def is_center(self):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > 3.8
    
    def annotated_eye(self, side: int = BOTH_EYES, line_size: int = 1) -> np.ndarray:
        """Returns the main frame with eyes highlighted"""
        frame = self.frame
        if not self.pupils_located:
            return frame

        color = (233, 128, 0)
        if side in [LEFT_EYE, BOTH_EYES]:
            pos1 = self.eye_left.origin
            pos2 = (pos1[0] + self.eye_left.center[0] * 2, pos1[1] + self.eye_left.center[1] * 2)
            cv2.rectangle(frame, pos1, pos2, color, line_size)
        if side in [RIGHT_EYE, BOTH_EYES]:
            pos1 = self.eye_right.origin
            pos2 = (pos1[0] + self.eye_right.center[0] * 2, pos1[1] + self.eye_right.center[1] * 2)
            cv2.rectangle(frame, pos1, pos2, color, line_size)

        return frame.copy()

    def annotated_pupil(self, side: int = BOTH_EYES, line_size: int = 1) -> np.ndarray:
        """Returns the main frame with pupils highlighted"""
        frame = self.frame
        if not self.pupils_located:
            return frame

        line_len = 3 + 2 * line_size

        color = (0, 255, 0)
        if side in [LEFT_EYE, BOTH_EYES]:
            x_left, y_left = self.pupil_left_coords()
            cv2.line(frame, (x_left - line_len, y_left), (x_left + line_len, y_left), color, line_size)
            cv2.line(frame, (x_left, y_left - line_len), (x_left, y_left + line_len), color, line_size)
        if side in [RIGHT_EYE, BOTH_EYES]:
            x_right, y_right = self.pupil_right_coords()
            cv2.line(frame, (x_right - line_len, y_right), (x_right + line_len, y_right), color, line_size)
            cv2.line(frame, (x_right, y_right - line_len), (x_right, y_right + line_len), color, line_size)

        return frame.copy()
    
    def annotated_frame(self, side: int = BOTH_EYES, line_size: int = 1) -> np.ndarray:
        if self.equalizehist == 1:
            self.frame = hisEqulColor(self.frame)
            self.equalizehist = 2

        self.annotated_eye(side, line_size)
        return self.annotated_pupil(side,  line_size)

    def show(self, win_name: str = "Demo") -> None:
        cv2.imshow(win_name, self.frame)
    
    def save(self, file_name: str, param = None) -> None:
        cv2.imwrite(file_name, self.frame, param)


class GazeTrackingFromVideo(GazeTracking):
    """
    This class inherits from 'GazeTracking'.
    It provides an encapsulation iter to read from VideoCapture.
    """
    __slots__ = ["capture", "flip"]

    def __init__(self, capture: Union[str, int] = 0, *, equalizehist: bool = False,  flip: bool = True):
        self.capture = cv2.VideoCapture(capture, cv2.CAP_DSHOW)
        self.flip = flip
        super().__init__(equalizehist=equalizehist)
    
    def __iter__(self) -> "GazeTrackingFromVideo":
        return self
    
    def __next__(self) -> np.ndarray:
        ret, raw_frame = self.capture.read()
        if not ret:
            raise StopIteration(raw_frame)
        
        if self.flip:
            raw_frame = cv2.flip(raw_frame, 1)
        
        self.refresh(raw_frame)
        return self.frame