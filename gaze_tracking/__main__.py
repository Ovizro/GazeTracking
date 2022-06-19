import sys
import cv2
from argparse import ArgumentParser

from . import GazeTracking, GazeTrackingFromVideo


def main(*argv: str) -> None:
    parse = ArgumentParser("gaze tracking")
    parse.add_argument("-i", "--image", help="the image path to track")
    parse.add_argument("-v", "--video", help="video path or ID of camera to track")
    parse.add_argument("-e", "--equalizehist", action="store_true")
    parse.add_argument("-f", "--flip", action="store_true", help="flip video frame")
    parse.add_argument("-o", "--output", help="output file name")
    parse.add_argument("--fourcc",
        help="video writer fourcc, only used when the output path is given",
        default="XVID", choices=["I420", "MJPG", "MP4V", "XVID", "PIMI", "FLVI", "DIVX"])

    args = parse.parse_args(argv)
    if args.image:
        gaze = GazeTracking(args.image, equalizehist=args.equalizehist)
        gaze.annotated_frame()
        if args.output:
            gaze.save(args.output)
        gaze.show()
        cv2.waitKey(0)
    if args.video or not args.image:
        if args.video is None:
            video = 0
        elif args.video.isdigit():
            video = int(args.video)
        else:
            video = args.video
        gaze = GazeTrackingFromVideo(video, equalizehist=args.equalizehist, flip=args.flip)
        fps = gaze.fps

        if args.output:
            fourcc = cv2.VideoWriter_fourcc(*args.fourcc)
            out = cv2.VideoWriter(args.output, fourcc, fps, (gaze.width, gaze.height), True)

        for _ in gaze:
            gaze.annotated_frame()
            if args.output:
                out.write(gaze.frame)
            gaze.show()
            
            if cv2.waitKey(max(1000 // fps, 10)) == 27:
                break
        
        gaze.release()
        if args.output:
            out.release()

main(*sys.argv[1:])