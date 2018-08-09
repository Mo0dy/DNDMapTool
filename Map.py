import numpy as np
import cv2 as cv
import DNDMapTool.ImProcessing as process


class Map(object):
    def __init__(self, name="default", img=None, nx=0, ny=0, mxl=0, mxr=0, myt=0, myb=0):
        self.name = name
        self.img = None
        self.grid = None  # the grid that is played in as a boolean image mask
        self.fog = None  # the alpha values for fow
        self.old_map = None  # the old map is used as a fow
        self.border = None  # this border can be used to i.e. add a red border for "unpaused"
        # the amount of cells
        self.nx = nx
        self.ny = ny

        # margins
        self.mxr = mxr
        self.mxl = mxl
        self.myt = myt
        self.myb = myb

        self.update_image(img)

    def update_grid(self):
        # a boolean array where the gridlinepixels are True
        self.grid = np.zeros(self.img.shape[:2]).astype(np.bool)
        for i in range(0, self.nx + 1):
            line_x = int(i * self.dx) + self.mxl
            self.grid[self.myt:-self.myb - 1, max(0, line_x - 1): min(line_x + 1, self.img.shape[1] - 1)] = True
        for j in range(0, self.ny + 1):
            line_y = int(j * self.dy) + self.myt
            self.grid[max(0, line_y - 1): min(line_y + 1, self.img.shape[0] - 1), self.mxl:-self.mxr - 1] = True

    # update the image and all other important things
    def update_image(self, n_img=None):
        if np.any(n_img):
            self.img = n_img.copy()
            self.update_squares()
        if np.any(self.img) and self.dx * self.dy:
            self.update_grid()
            self.update_border()
            self.fog = np.ones(self.img.shape[:2]) * 255  # alpha values for adding the fow onto the map
            self.update_fow_map()

    def update_squares(self):
        # tilesize
        if self.nx:
            self.dx = (self.img.shape[1] - self.mxl - self.mxr) / self.nx
        if self.ny:
            self.dy = (self.img.shape[0] -self. myt - self.myb) / self.ny
        self.update_grid()

    def update_border(self, b_thickness=3):
        # create the border
        # the border thickness
        self.border = np.ones(self.img.shape[:2]).astype(np.bool)
        self.border[b_thickness:-b_thickness - 1, b_thickness:-b_thickness - 1] = False

    def update_fow_map(self):
        from DNDMapTool.RecourceManager import load_img
        self.old_map = cv.resize(load_img("OldMap"), (self.img.shape[1], self.img.shape[0]))

    def px_to_coor(self, x, y):
        # returns coor in j, i
        return [int((y - self.myt) // self.dy), int((x - self.mxl) // self.dx)]

    def coor_to_px_mid(self, coor):
        j, i = coor
        return int((i + 0.5) * self.dx) + self.mxl, int((j + 0.5) * self.dy) + self.myt

    def clear_fog(self, coor, rad):
        cv.circle(self.fog, (coor[1], coor[0]), rad, 0, -1)

    def add_fog(self, coor, rad):
        cv.circle(self.fog, (coor[1], coor[0]), rad, 255, -1)

    # returns the mapimage (kwargs can modify the image: gridlines, grid_color, fow)
    def get_img(self, **kwargs):
        t_img = self.img.copy()
        if "gridlines" in kwargs.keys() and kwargs["gridlines"]:
            if "grid_color" in kwargs.keys() and kwargs["grid_color"]:
                color = kwargs["grid_color"]
            else:
                color = (50, 50, 50)  # standard gray color
            t_img[self.grid] = color  # self.grid holds a boolean array in which the gridlines are predrawn
        if "fow" in kwargs.keys():
            if kwargs["fow"].lower() == "tv":
                # t_img = process.alpha_blend(self.old_map, t_img, cv.GaussianBlur(self.fog, (101, 101), 0))
                process.alpha_blend_nb(self.old_map, t_img, cv.GaussianBlur(self.fog, (101, 101), 0))
            elif kwargs["fow"].lower() == "gm":
                t_img[self.fog.astype(np.bool)] //= 2  # make the fow regions darker for gm
        if "border" in kwargs and kwargs["border"]:
            # add red border
            t_img[self.border, :2] = 0
            t_img[self.border, 2] = 255
        return t_img