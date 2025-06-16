import numpy as np
import tkinter as tk
from itertools import product
from PIL import Image, ImageTk
from tkinter import simpledialog, ttk
from typing import Optional


def parse(s: str) -> Optional[float]:
    x = [float(n) for n in s.split()]
    match len(x):
        case 1:
            return x[0]
        case 2:
            return x[0] + x[1] / 60.0
        case 3:
            return x[0] + x[1] / 60.0 + x[2] / 3600.0
    return None


def tohex(rgb: tuple[int]) -> str:
    s = "#"
    for i in range(len(rgb)):
        s += f"{rgb[i]:02x}"
    return s


class Tool(tk.Toplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.attributes("-type", "dialog")
        self.title(title)


class MagnifyingTool(Tool):
    def __init__(self, master, color="#333333"):
        super().__init__(master, "Magnify")
        # self.overrideredirect(True)
        self.color = color
        self.resizable(False, False)
        self.pane = tk.Canvas(self, width=256, height=256)
        self.pane.pack(fill=tk.BOTH, expand=True)

    def update(self, image):
        self.pane.create_image(0, 0, anchor=tk.NW, image=image)
        self.pane.create_line(116, 128, 140, 128, width=2, fill=self.color)
        self.pane.create_line(128, 116, 128, 140, width=2, fill=self.color)


class ImageView(tk.Label):
    x: int = 0
    y: int = 0
    i: int = 0
    j: int = 0

    def __init__(self, master, name, callback, status):
        super().__init__(master)
        self.configure(background="black", cursor="dotbox", padx=0, pady=0)
        self.win = MagnifyingTool(self)
        self.callback = callback
        self.status = status
        with Image.open(name) as im:
            self.im = im.copy()
        self.bind("<Configure>", self._resize)
        self.bind("<Button-1>", self.action)
        self.bind("<space>", self.action)
        self.bind("<Motion>", self._motion)

    def action(self, ev):
        self.callback(self.i, self.j, self.color())

    def color(self):
        w, h = self.im.size
        if 0 <= self.i < w and 0 <= self.j < h:
            return self.im.getpixel((self.i, self.j))
        return None

    def magnify(self):
        self.i, self.j = self.tr(self.x, self.y)
        w, h = self.im.size
        if 0 <= self.i < w and 0 <= self.j < h:
            im = self.im.crop((self.i - 32, self.j - 32, self.i + 32, self.j + 32))
            self.mag = ImageTk.PhotoImage(
                im.resize((256, 256), Image.Resampling.NEAREST)
            )
            self.win.update(self.mag)
            self.status.set_coords(self.i, self.j)
            self.status.set_color(self.color())

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        self.magnify()

    def tr(self, x, y):
        w_im, h_im = self.photo.width(), self.photo.height()
        w, h = self.im.size
        p, q = w / w_im, h / h_im
        return round(p * x), round(q * y)

    def _motion(self, ev):
        self.x, self.y = ev.x - self.dx, ev.y - self.dy
        self.magnify()

    def _resize(self, ev):
        w, h = ev.width, ev.height
        w_im, h_im = self.im.size
        a = w / h
        a_im = w_im / h_im
        w_im, h_im = w, h
        if a < a_im:
            h_im = round(w_im / a_im)
        else:
            w_im = round(h_im * a_im)
        self.dx = max(w - w_im, 0) // 2
        self.dy = max(h - h_im, 0) // 2
        im = self.im.resize((w_im, h_im), Image.Resampling.NEAREST)
        self.photo = ImageTk.PhotoImage(im)
        self.configure(image=self.photo)


class Statusbar(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=4)
        self.coords = tk.StringVar()
        ttk.Label(self, textvariable=self.coords, width=12).pack(side=tk.LEFT)
        self.color = ttk.Label(self, width=14)
        self.color.pack(side=tk.LEFT)
        self.mode = tk.StringVar()
        self.set_mode("none")
        ttk.Label(self, textvariable=self.mode, width=6).pack(side=tk.RIGHT)
        ttk.Label(self, text="MODE:").pack(side=tk.RIGHT)

    def set_mode(self, m):
        self.mode.set(m.upper())

    def set_color(self, rgb):
        self.color.configure(
            text=f"rgb({rgb[0]:3d},{rgb[1]:3d},{rgb[2]:3d})", background=tohex(rgb)
        )

    def set_coords(self, i, j):
        self.coords.set(f"{i}, {j}")


class App(ttk.Frame):
    clrs: list = []
    x: list = []
    y: list = []
    mode: int = 0

    def __init__(self, title, mode="single"):
        super().__init__(tk.Tk())
        assert mode in ["single", "both"]
        self.master.wm_title(title)
        self.master.option_add("*tearOff", tk.FALSE)

        self.statusbar = Statusbar(self)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.view = ImageView(self, "ref.ppm", self.onaction, self.statusbar)
        self.view.pack(fill=tk.BOTH, expand=True)

        self.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.master.bind_all("<Control-q>", lambda e: self.master.destroy())
        self.master.bind_all("<Control-s>", self.save)
        self.master.bind_all("<Up>", lambda e: self.view.shift(0, -1))
        self.master.bind_all("<Down>", lambda e: self.view.shift(0, 1))
        self.master.bind_all("<Left>", lambda e: self.view.shift(-1, 0))
        self.master.bind_all("<Right>", lambda e: self.view.shift(1, 0))
        self.master.bind_all("<a>", self.view.action)
        self.master.bind_all("<Escape>", lambda e: self.set_mode(0))
        self.master.bind_all("<x>", lambda e: self.set_mode(1))
        self.master.bind_all("<y>", lambda e: self.set_mode(2))
        self.master.bind_all("<c>", lambda e: self.set_mode(3))

        self.mutex = mode

    def _askcoordinate(self, t, x):
        ans = simpledialog.askstring(
            "Add Ground Control Point", f"{t.upper()}-Coordinate ({x}):"
        )
        if ans:
            getattr(self, t).append((x, parse(ans)))

    def onaction(self, i, j, rgb):
        match self.mode:
            case 0:
                return
            case 1:
                self._askcoordinate("x", i)
                if self.mutex == "both":
                    self._askcoordinate("y", j)
            case 2:
                if self.mutex == "both":
                    return
                self._askcoordinate("y", j)
            case 3:
                self.clrs.append(rgb)

    def run(self):
        self.master.mainloop()

    def save(self, e):
        xy = zip(self.x, self.y) if self.mutex == "both" else product(self.x, self.y)
        with open("gcp.txt", "x") as f:
            for wa in xy:
                s = "\t".join([str(n) for n in np.transpose(wa).flatten()])
                f.write(s + "\n")
        with open("colors.txt", "x") as f:
            for rgb in self.clrs:
                f.write(tohex(rgb) + "\n")

    def set_mode(self, m):
        modes = ["none", "x", "y", "color"]
        assert 0 <= m < len(modes)
        self.mode = m
        self.statusbar.set_mode(modes[m])


def main():
    app = App("IMapRef")
    app.run()
    return 0
