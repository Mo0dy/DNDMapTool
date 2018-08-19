import numpy as np
import cv2 as cv
import DNDMapTool.ImProcessing as process
import time


class Map(object):
    def __init__(self, name="default", img=None, nx=0, ny=0, mxl=0, mxr=0, myt=0, myb=0):
        self.name = name
        self.dm_img = None
        self.img = None
        self.grid = None  # the grid that is played in as a boolean image mask
        self.fog = None  # the alpha values for fow
        self.old_map = None  # the old map is used as a fow
        self.border = None  # this border can be used to i.e. add a red border for "unpaused"
        # the amount of cells
        self.nx = nx
        self.ny = ny

        self.dx = None
        self.dy = None

        # margins
        self.mxr = mxr
        self.mxl = mxl
        self.myt = myt
        self.myb = myb

        self.update_image(img)

        self.tokens = {}  # the player grid and the tokens hold the same information. here every token is associated with a position
        self.play_grid = None  # the actual grid that gets played in. each cell can hold one piece

    # add token to both the tokens dict and the play grid
    def add_token(self, token, pos):
        self.tokens[token] = pos
        self.play_grid[pos[0]][pos[1]] = token

    # remove token from both the tokens dict and the play grid
    def remove_token(self, token):
        self.play_grid[self.tokens[token][0]][self.tokens[token][1]] = None
        del self.tokens[token]

    def token_at(self, gridpos):  #returns token at y and x pos
        return self.play_grid[gridpos[0]][gridpos[1]]

    def move_token(self, token, n_pos):
        self.play_grid[self.tokens[token][0]][self.tokens[token][1]] = None
        self.tokens[token] = n_pos
        self.play_grid[self.tokens[token][0]][self.tokens[token][1]] = token

    def update_grid(self):
        self.play_grid = [[None] * self.nx for _ in range(self.ny)]
        # a boolean array where the gridlinepixels are True
        self.grid = np.zeros(self.dm_img.shape[:2]).astype(np.bool)
        for i in range(0, self.nx + 1):
            line_x = int(i * self.dx) + self.mxl
            self.grid[self.myt:-self.myb - 1, max(0, line_x - 1): min(line_x + 1, self.dm_img.shape[1] - 1)] = True
        for j in range(0, self.ny + 1):
            line_y = int(j * self.dy) + self.myt
            self.grid[max(0, line_y - 1): min(line_y + 1, self.dm_img.shape[0] - 1), self.mxl:-self.mxr - 1] = True

    # update the image and all other important things
    def update_image(self, n_img=None):
        if np.any(n_img):
            self.img = n_img.copy()
            self.update_fow_map()
            self.fog = np.ones(self.dm_img.shape[:2]) * 255  # alpha values for adding the fow onto the map
            self.update_border()
        if np.any(self.img) and self.nx * self.ny:
            self.update_squares()

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
        self.border = np.ones(self.dm_img.shape[:2]).astype(np.bool)
        self.border[b_thickness:-b_thickness - 1, b_thickness:-b_thickness - 1] = False

    def update_fow_map(self):
        from DNDMapTool.RecourceManager import load_img
        self.old_map = cv.resize(load_img("OldMap")[0], (self.dm_img.shape[1], self.dm_img.shape[0]))

    def px_to_coor(self, x, y):
        # returns coor in j, i
        if self.dx and self.dy:
            return [int((y - self.myt) // self.dy), int((x - self.mxl) // self.dx)]
        else:
            return int(x), int(y)

    def coor_to_px_mid(self, coor):
        j, i = coor
        if self.dx and self.dy:
            return int((j + 0.5) * self.dy) + self.myt, int((i + 0.5) * self.dx) + self.mxl
        else:
            return coor

    def clear_fog(self, coor, rad):
        cv.circle(self.fog, (coor[1], coor[0]), rad, 0, -1)

    def add_fog(self, coor, rad):
        cv.circle(self.fog, (coor[1], coor[0]), rad, 255, -1)

    # returns the mapimage (kwargs can modify the image: gridlines, grid_color, fow)
    def get_img(self, **kwargs):
        # if dm image is requested
        zoomed_main = False
        if "dm" in kwargs and kwargs["dm"] and np.any(self.dm_img):
            t_img = self.dm_img.copy()
        else:
            # zoom
            if "trans_x" in kwargs:
                offset_x = int(kwargs["trans_x"] * self.img.shape[1])
            else:
                offset_x = 0

            if "trans_y" in kwargs:
                offset_y = int(kwargs["trans_y"] * self.img.shape[0])
            else:
                offset_y = 0

            if "zoom" in kwargs:
                zoomed_main = True
                zoom = kwargs["zoom"]
                dx = self.img.shape[1] / zoom
                dy = self.img.shape[0] / zoom
                x_min = int((self.img.shape[1] - dx) / 2) + offset_x
                x_max = int(x_min + dx)
                y_min = int((self.img.shape[0] - dy) / 2) + offset_y
                y_max = int(y_min + dy)

                # clip
                x_min = max(0, x_min)
                x_min = min(self.img.shape[1], x_min)
                x_max = min(self.img.shape[1], x_max)
                x_max = max(x_max, 0)

                y_min = max(0, y_min)
                y_min = min(self.img.shape[0], y_min)
                y_max = min(self.img.shape[0], y_max)
                y_max = max(y_max, 0)

                t_img = cv.resize(self.img[y_min:y_max, x_min:x_max], (self.dm_img.shape[1], self.dm_img.shape[0]))
            else:
                t_img = self.limit_size(self.img)
        img_size = t_img.shape[:2]
        if "gridlines" in kwargs.keys() and kwargs["gridlines"]:
            # make sure there is a grid for this image
            if np.any(self.grid):
                if "grid_color" in kwargs.keys() and kwargs["grid_color"]:
                    color = kwargs["grid_color"]
                else:
                    color = (50, 50, 50)  # standard gray color
                t_img[self.grid] = color  # self.grid holds a boolean array in which the gridlines are predrawn
        if "tokens" in kwargs.keys() and kwargs["tokens"]:
            # display tokens
            for t, grid_pos in self.tokens.items():
                pos = self.coor_to_px_mid(grid_pos)  # this also needs to be transformed
                # use dx and dy if gridlines are allowed
                if self.dx and self.dy:
                    dx = self.dx
                    dy = self.dy
                else:
                    dx = 100
                    dy = 100
                t.blit(t_img, pos, dx, dy)
        if "fow" in kwargs.keys():
            if kwargs["fow"].lower() == "tv":
                # t_img = process.alpha_blend(self.old_map, t_img, cv.GaussianBlur(self.fog, (101, 101), 0))#
                my_fog =  cv.GaussianBlur(self.fog, (101, 101), 0)
                if zoomed_main:
                    # transfrom fog to fit with the transformed img:
                    x_min_fog = int(x_min / self.img.shape[0] * self.fog.shape[0])
                    x_max_fog = int(x_max / self.img.shape[0] * self.fog.shape[0])
                    y_min_fog = int(y_min / self.img.shape[0] * self.fog.shape[0])
                    y_max_fog = int(y_max / self.img.shape[0] * self.fog.shape[0])
                    my_fog = cv.resize(my_fog[y_min_fog:y_max_fog, x_min_fog:x_max_fog], (t_img.shape[1], t_img.shape[0]))
                process.alpha_blend_nb(self.old_map, t_img, my_fog)
            elif kwargs["fow"].lower() == "gm":
                # t_img[self.fog.astype(np.bool)] //= 2  # make the fow regions darker for gm
                process.darken_maks(t_img, self.fog)
        if "border" in kwargs and kwargs["border"]:
            # add red border
            t_img[self.border, :2] = 0
            t_img[self.border, 2] = 255
        if "dm" in kwargs and kwargs["dm"] and "zoom" in kwargs:
            if "trans_x" in kwargs:
                offset_x = int(kwargs["trans_x"] * self.dm_img.shape[1])
            else:
                offset_x = 0

            if "trans_y" in kwargs:
                offset_y = int(kwargs["trans_y"] * self.dm_img.shape[0])
            else:
                offset_y = 0

            zoom = kwargs["zoom"]
            dx = self.dm_img.shape[1] / zoom
            dy = self.dm_img.shape[0] / zoom
            x_min = int((self.dm_img.shape[1] - dx) / 2) + offset_x
            x_max = int(x_min + dx)
            y_min = int((self.dm_img.shape[0] - dy) / 2) + offset_y
            y_max = int(y_min + dy)

            # clip
            x_min = max(0, x_min)
            x_min = min(self.dm_img.shape[1], x_min)
            x_max = min(self.dm_img.shape[1], x_max)
            x_max = max(x_max, 0)

            y_min = max(0, y_min)
            y_min = min(self.dm_img.shape[0], y_min)
            y_max = min(self.dm_img.shape[0], y_max)
            y_max = max(y_max, 0)

            cv.rectangle(t_img, (x_min, y_min), (x_max, y_max), (255, 255, 0), 2, cv.LINE_AA)

        return t_img

    def limit_size(self, img):
        fx = 1920 / img.shape[1]
        fy = 1080 / img.shape[0]
        # scale to the smaller factor
        f = min(fx, fy)
        return cv.resize(img, (0, 0), fx=f, fy=f)