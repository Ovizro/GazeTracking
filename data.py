from tkinter import messagebox
import cv2
import pandas as pd
from random import randint
from tkinter import *
from typing import List, Optional

from gaze_tracking import GazeTrackingFromVideo

COUNT = 500

gaze = GazeTrackingFromVideo(1, flip=True)

data = pd.DataFrame(
    index=pd.RangeIndex(1, COUNT + 1), 
    columns=[
        "focus.x", "focus.y", "l_pupil.x","l_pupil.y", "r_pupil.x", "r_pupil.y",
        "l_eye.x", "l_eye.y", "r_eye.x", "r_eye.y"
    ]
)


def main() -> None:
    tk = Tk()
    tk.title("Data colletion")
    tk.attributes("-fullscreen", True)

    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()

    c_main = Canvas(tk, width=width, height=height, bg="#FFFFFF")

    CYC_SIZE = 20
    center_x = width // 2
    center_y = height // 2
    cyc = c_main.create_oval(
        center_x - CYC_SIZE, center_y - CYC_SIZE, center_x + CYC_SIZE, center_y + CYC_SIZE, fill="yellow")

    i = 1
    def update(event: Event):
        nonlocal center_x, center_y, i
        next(gaze)
        if not gaze.pupils_located:
            return

        l_pupil = gaze.pupil_left_coords()
        r_pupil = gaze.pupil_right_coords()

        d = data.loc[i]
        l_eye = gaze.eye_left
        r_eye = gaze.eye_right
        if i <= COUNT // 2:
            d["focus.x"] = center_x
            d["focus.y"] = center_y
        d["l_pupil.x"] = l_pupil[0]
        d["l_pupil.y"] = l_pupil[1]
        d["r_pupil.x"] = r_pupil[0]
        d["r_pupil.y"] = r_pupil[1]
        d["l_eye.x"] = l_eye.origin[0] + l_eye.center[0]
        d["l_eye.y"] = l_eye.origin[1] + l_eye.center[1]
        d["r_eye.x"] = r_eye.origin[0] + r_eye.center[0]
        d["r_eye.y"] = r_eye.origin[1] + r_eye.center[1]
        d["l_eye_s.x"] = l_eye.center[0] * 2
        d["l_eye_s.y"] = l_eye.center[1] * 2
        d["r_eye_s.x"] = r_eye.center[0] * 2
        d["r_eye_s.y"] = r_eye.center[1] * 2

        i += 1
        if i > COUNT:
            c_exit()
        elif i > COUNT // 2:
            c_main.delete(cyc)
            c_main.create_text(width // 2, height // 2, text="接下来请不要注视屏幕并按下Enter")
        else:
            center_x = randint(5, width - 5)
            center_y = randint(5, height - 5)
            c_main.coords(cyc, (center_x - CYC_SIZE, center_y - CYC_SIZE, center_x + CYC_SIZE, center_y + CYC_SIZE))
    
    c_main.pack(fill='both')

    def c_exit(evemt: Optional[Event] = None) -> None:
        if i <= COUNT:
            ans = messagebox.askyesno("Data collection unfinished", "Do you want to quit now?")
            if not ans:
                return
        data.to_excel("data.xlsx")
        tk.destroy()
    tk.bind_all("<KeyRelease-Q>", c_exit)
    tk.bind_all("<KeyRelease-q>", c_exit)
    tk.bind_all("<Escape>", c_exit)
    tk.bind_all("<Return>", update, add=True)

    c_main.focus()
    tk.mainloop()

if __name__ == "__main__":
    main()