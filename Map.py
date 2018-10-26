import numpy as np
import cv2 as cv
import DNDMapTool.ImProcessing as process
import time


class Map(object):
    """The map object stores all game information that is confined to a certain map.

    This includes map settings such as fog and the grid.
    This also includes all tokens etc."""

    def __init__(self, name="default", img=None, nx=0, ny=0, mxl=0, mxr=0, myt=0, myb=0):
        """
        :param name: The name of the map.
        :param img: The actual graphical map.
        :param nx: The amount of cells in x direction.
        :param ny: The amount of cells in y direction.
        :param mxl: The margin on the left.
        :param mxr: The margin on the right.
        :param myt: The margin on the top.
        :param myb: The margin on the bottom
        """
        self.name = name
        self.dm_img = None  # a seperate image that is shown for the dm instead of the normal map
        self.img = None  # the image of the map. this will be assigned with the update_image function
        self.fog = None  # the alpha values for fow
        # the old map image is used as a fow. the fow image can be changed from map to map and needs to be the same
        # size as the actual map
        self.old_map = None
        self.border = None  # this border can be used to i.e. add a red border for "unpaused"

        # information of the scale.
        self.y_pxper5feet = None
        self.x_pxper5feet = None

        # grid settings =====================================
        # the grid is currently not in use but can be used to confine tokens to cells / measure distances reliably etc.
        # later on I want to add range finders that might use this (or direct pixel) as basis
        self.grid = None  # the grid that is used in as a boolean image mask (actual visual interpretation of the grid)
        self.nx = nx
        self.ny = ny

        # the size of the gridcells
        self.dx = None
        self.dy = None

        # margins
        self.mxr = mxr
        self.mxl = mxl
        self.myt = myt
        self.myb = myb

        # do a lot of stuff that is needed to prepare a lot of the variables connected to the image and visual side
        self.update_image(img)

        # holds all tokens (key = token, value = position)
        # if the tokens are confined to a grid they should also be saved there to make interactions more direct
        self.tokens = {}

    def add_token(self, token, pos):
        """add token to both the tokens dict and the play grid"""
        self.tokens[token] = pos

    def remove_token(self, token):
        """remove token from the token dictionary"""
        del self.tokens[token]

    def token_at(self, px, py):
        """returns token at y and x pos (a token has a size as long as px, py is in it it will be returned)"""
        for t, pos in self.tokens.items():
            # rectangular collision check
            if pos[1] - t.sx / 2 < px < pos[1] + t.sx / 2 and pos[0] - t.sy / 2 < py < pos[0] + t.sy / 2:
                return t

    def move_token(self, token, n_pos):
        """change the position of a token"""
        self.tokens[token] = n_pos

    def token_pos(self, token):
        """get the position of a token"""
        return self.tokens[token]

    # some of the update functions. (calculate visuals from parameters / the self.img varaible)
    def update_grid(self):
        """creates the grid mask"""
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
        """assign values to the img, fow, border and if viable the grid"""
        if np.any(n_img):
            self.img = n_img.copy()
            self.update_fow_map()
            self.fog = np.ones(self.dm_img.shape[:2]) * 255  # alpha values for adding the fow onto the map
            self.update_border()
        if np.any(self.img) and self.nx * self.ny:  # if there is an image and viable grid settings (e.g. nx > 0 and ny > 0)
            self.update_squares()

    def update_squares(self):
        """calculate dx, dy and create the grid"""
        # tilesize
        if self.nx:
            self.dx = (self.img.shape[1] - self.mxl - self.mxr) / self.nx
        if self.ny:
            self.dy = (self.img.shape[0] -self. myt - self.myb) / self.ny
        self.update_grid()

    def update_border(self, b_thickness=3):
        """create the border"""
        self.border = np.ones(self.dm_img.shape[:2]).astype(np.bool)  # create a boolean array
        self.border[b_thickness:-b_thickness - 1, b_thickness:-b_thickness - 1] = False  # exclude the center region

    def update_fow_map(self):
        """load and resize the "oldmap" image"""
        from DNDMapTool.RecourceManager import load_img
        self.old_map = cv.resize(load_img("OldMap")[0], (self.dm_img.shape[1], self.dm_img.shape[0]))

    def px_to_coor(self, x, y):
        """returns the grid coordinates of the current pixel input"""
        if self.dx and self.dy:
            return [int((y - self.myt) // self.dy), int((x - self.mxl) // self.dx)]
        else:
            return int(x), int(y)

    def coor_to_px_mid(self, coor):
        """returns the midpoint of the input grid coordinates"""
        j, i = coor
        if self.dx and self.dy:
            return int((j + 0.5) * self.dy) + self.myt, int((i + 0.5) * self.dx) + self.mxl
        else:
            return coor

    def clear_fog(self, coor, rad):
        """clear the fog in a certain radius around px coordinates"""
        cv.circle(self.fog, (coor[1], coor[0]), rad, 0, -1)

    def add_fog(self, coor, rad):
        """add fog in a certain radius around px coordinates"""
        cv.circle(self.fog, (coor[1], coor[0]), rad, 255, -1)

    def get_img(self, **kwargs):
        """returns the mapimage (kwargs can modify the image: gridlines, grid_color, fow).

        This is the main rendering function that gets invoked by the viewer"""

        # now follows a bunch of random code that probably should be cleaned up a bit
        # especially the translation / zoom functionality should also allow for affine translations of single points
        # from the dm window (normal full image) to the zoomed version in a natural way (for pings etc)
        # scale factor
        sfx = 1
        sfy = 1

        # this checks the different kwargs.
        # first check if there is the kwarg then check if it is true. this avoids errors because the second check
        # of an and statement will be ignored if the first one is false:
        # if "kwarg" in kwargs and kwargs["kwarg"]:
        # alternatively:
        # if "kwarg" in kwargs.keys() and kwarg["kwarg"]:

        # choose the correct image either the dm or the normal map image.
        if "dm" in kwargs and kwargs["dm"] and np.any(self.dm_img):
            t_img = self.dm_img.copy()
        else:  # if the normal map is chosen determine its scale relative to the dm window
            t_img = self.img.copy()
            sfx = t_img.shape[1] / self.dm_img.shape[1]
            sfy = t_img.shape[0] / self.dm_img.shape[0]

        # blit tokens:
        if "tokens" in kwargs.keys() and kwargs["tokens"]:
            # display tokens
            for t, pos in self.tokens.items():
                # use dx and dy if gridlines are allowed (this should be added later on)
                # blit does an alphaplit of one image onto another
                t.blit(t_img, (int(pos[0] * sfy), int(pos[1] * sfx)), int(t.sx * sfx), int(t.sy * sfy))

        zoomed_main = False  # remember if main has been zoomed. this could be replaced by "zoom" in kwargs
        if not ("dm" in kwargs and kwargs["dm"] and np.any(self.dm_img)):  # only the normal map can be zoomed
            # calculate translation
            if "trans_x" in kwargs:
                offset_x = int(kwargs["trans_x"] * self.img.shape[1])
            else:
                offset_x = 0

            if "trans_y" in kwargs:
                offset_y = int(kwargs["trans_y"] * self.img.shape[0])
            else:
                offset_y = 0

            # actual zoom (also add translation) by choosing a part of the image (indexing) and resizing it to full hd
            if "zoom" in kwargs:
                zoomed_main = True
                zoom = kwargs["zoom"]  # get the zoom factor. larger means a smaller image
                dx = self.img.shape[1] / zoom
                dy = self.img.shape[0] / zoom

                # calculate minimum and maximum indices
                x_min = int((self.img.shape[1] - dx) / 2) + offset_x
                x_max = int(x_min + dx)
                y_min = int((self.img.shape[0] - dy) / 2) + offset_y
                y_max = int(y_min + dy)

                # clip (the way the image gets currently clipped means a stretching close to the border)
                # the other option is to clip both the smallest and largest values
                x_min = max(0, x_min)
                x_min = min(self.img.shape[1], x_min)
                x_max = min(self.img.shape[1], x_max)
                x_max = max(x_max, 0)

                y_min = max(0, y_min)
                y_min = min(self.img.shape[0], y_min)
                y_max = min(self.img.shape[0], y_max)
                y_max = max(y_max, 0)

                # actual resizing
                t_img = cv.resize(t_img[y_min:y_max, x_min:x_max], (self.dm_img.shape[1], self.dm_img.shape[0]))
            else:
                # no zooming. simpler resizing to max full hd
                t_img = self.limit_size(t_img)

        # overlay gridlines
        if "gridlines" in kwargs.keys() and kwargs["gridlines"]:
            # make sure there is a grid for this image
            if np.any(self.grid):  # check if there is information in the grid template
                if "grid_color" in kwargs.keys() and kwargs["grid_color"]:
                    color = kwargs["grid_color"]
                else:
                    color = (50, 50, 50)  # standard gray color
                # draw grid onto image using a flat color
                t_img[self.grid] = color  # self.grid holds a boolean array in which the gridlines are predrawn

        # add fog of war using alphablit
        if "fow" in kwargs.keys():
            # there are two different versions of the fog. a simple darker one for the dm window and a more elaborate
            # one for the main window e.g. "tv" window
            if kwargs["fow"].lower() == "tv" or kwargs["fow"].lower() == "main":
                # blur the fogmap (the edges will be fuzzy)
                # this should not be done every drawing call. the best option would be to draw a fuzzy circle in the
                # first place. this is one of the main reasons for slow drawing
                my_fog = cv.GaussianBlur(self.fog, (101, 101), 0)

                # if the main window is zoomed the fog also needs to be resized
                if zoomed_main:
                    # transfrom fog to fit with the transformed img using the information from above:
                    # for all transformations there should be one function!
                    x_min_fog = int(x_min / self.img.shape[0] * self.fog.shape[0])
                    x_max_fog = int(x_max / self.img.shape[0] * self.fog.shape[0])
                    y_min_fog = int(y_min / self.img.shape[0] * self.fog.shape[0])
                    y_max_fog = int(y_max / self.img.shape[0] * self.fog.shape[0])
                    my_fog = cv.resize(my_fog[y_min_fog:y_max_fog, x_min_fog:x_max_fog], (t_img.shape[1], t_img.shape[0]))
                process.alpha_blend_nb(self.old_map, t_img, my_fog)  # the actual alphablending of the image
            elif kwargs["fow"].lower() == "gm":  # a simpler faster transparent fow
                process.darken_maks(t_img, self.fog)  # darken the region that is in fog

        # add a red border
        if "border" in kwargs and kwargs["border"]:
            # add red border
            t_img[self.border, :2] = 0
            t_img[self.border, 2] = 255
        # add a rectangle that shows the are that is being  displayed in the main window
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
        """limit the size of an image to 1920x1080"""
        fx = 1920 / img.shape[1]
        fy = 1080 / img.shape[0]
        # scale to the smaller factor
        f = min(fx, fy)
        return cv.resize(img, (0, 0), fx=f, fy=f)