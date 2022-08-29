import copy
import glob
import json
import os
import tkinter
from collections import deque

from PIL import Image, ImageTk


class App(tkinter.Frame):
    class Face:
        def __init__(self, a):
            self.ind = 0
            self.face_parts = {
                'eye_side': a.FacePart(2, 'green'),
                'mouth_side': a.FacePart(2, 'green'),
                'nose_side': a.FacePart(2, 'green'),
                'l_eye_w': a.FacePart(2, 'red'),
                'l_eye_h': a.FacePart(2, 'red'),
                'r_eye_w': a.FacePart(2, 'red'),
                'r_eye_h': a.FacePart(2, 'red'),
                'mouth_w': a.FacePart(2, 'blue'),
                'mouth_h': a.FacePart(2, 'blue'),
                'jaw': a.FacePart(1, 'yellow'),
                'nose_w': a.FacePart(2, 'yellow'),
                'nose_h': a.FacePart(2, 'yellow')
            }
            self.part = self.face_parts['eye_side']

        def point(self, p):
            self.part.list.append((p.x, p.y))
            if self.part.is_full() and self.ind < len(self.face_parts) - 1:
                self.ind += 1
                key = list(self.face_parts)[self.ind]
                self.part = self.face_parts[key]
                print(f'part={key}')

        def is_completed(self):
            return self.part.is_full() and self.ind == len(self.face_parts) - 1

    class FacePart:
        def __init__(self, max_len, color):
            self.max_len = max_len
            self.list = []
            self.color = color

        def is_full(self):
            return len(self.list) == self.max_len

    class Point:
        def __init__(self, a, x, y, color):
            self.r = 3
            self.app = a
            self.x = x
            self.y = y
            x1 = x - self.r
            y1 = y - self.r
            x2 = x + self.r
            y2 = y + self.r
            app.canvas.create_oval(x1, y1, x2, y2, tag='circle', fill=color, outline='')

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.files = deque(glob.glob("./images/*"))
        self.file = self.files.pop()
        self.face = self.Face(self)

        self.width = 500
        self.height = 500
        self.master.geometry(f'{self.width}x{self.height}')
        self.master.resizable(False, False)

        img = Image.open(self.file)
        w, h = img.size

        im_w = self.width if w > h else self.height * w / h
        im_h = self.height if h > w else self.width * h / w
        #500 : h = x : w
        #hx = 500w
        #x = 500w/h
        print(im_w)
        print(im_h)
        img = img.resize((int(im_w), int(im_h)))
        self.img = ImageTk.PhotoImage(img, master=self)

        self.canvas = tkinter.Canvas(self.master, width=self.width, height=self.height)
        self.canvas.place(x=0, y=0)

        self.item = self.canvas.create_image(0, 0, image=self.img, anchor=tkinter.NW)
        self.canvas.bind('<ButtonPress-1>', self.detect)

    def sw_img(self, source):
        w, h = source.size
        im_w = self.width if w > h else self.height * w / h
        im_h = self.height if h > w else self.width * h / w

        img = source.resize((int(im_w), int(im_h)))
        self.img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.item, image=self.img)

    def detect(self, event):
        print(f'x={event.x}, y={event.y}')
        p = self.Point(self, event.x, event.y, self.face.part.color)
        self.face.point(p)
        if self.face.is_completed():
            self.output()
            self.canvas.delete('circle')
            if len(self.files) == 0:
                self.master.destroy()
            else:
                self.file = self.files.pop()
                self.sw_img(Image.open(self.file))
                self.face = self.Face(self)
                print('switched')

    def output(self):
        data = copy.copy(self.face.face_parts)
        for k, v in data.items():
            data[k] = v.list

        filename = os.path.splitext(os.path.basename(self.file))[0]
        file = open(f'./data/{filename}.json', mode='w')
        json.dump(data, file, ensure_ascii=False)
        file.close()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = App(master=root)
    app.mainloop()
