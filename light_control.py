#-*- coding : utf-8-*-
# coding:unicode_escape

import sys
import cv2
from argparse import ArgumentParser
from gaze_tracking import GazeTrackingFromVideo
from screen_brightness_control import set_brightness

parse = ArgumentParser()
parse.add_argument("-v", "--videocapture", default=0, type=int, help="camera id")
parse.add_argument("-e", "--equalizehist", action="store_true")
parse.add_argument("-f", "--flip", action="store_true", help="flip video frame")
parse.add_argument("-s", "--show", action="store_true")

args = parse.parse_args()

gaze = GazeTrackingFromVideo(
    args.videocapture, equalizehist=args.equalizehist, flip=args.flip)

count = 0

try:
    for _ in gaze:
        if gaze.pupils_located:
            if count < 5:
                count += 1
            else:
                set_brightness("+5")
        else:
            if count > 0:
                count -= 1
            else:
                set_brightness("-5")
        
        if args.show:
            gaze.annotated_frame()
            gaze.show()
        
        if cv2.waitKey(1000) == 27:
            break
except (KeyboardInterrupt):
    gaze.release()
    sys.exit()