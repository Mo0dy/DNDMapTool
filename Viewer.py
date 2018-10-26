import cv2 as cv
from DNDMapTool.Game import Game
import numpy as np
import time


"""The viewer displays the main map and gm map according to parameters that can be set."""


# the properties that can be changes
PROP_VIEW = 0  # the current view
PROP_MAP = 1  # the current map
PROP_GRIDLINES = 2  # show gridlines (boolean)
PROP_PLAYERS = 3  # show players
PROP_UPDATE_MAIN = 4  # should the main window be updated?
PROP_GM_VIEW = 5  # the current state of the gm view
PROP_SHOW_TOKEN = 6
# first translated then zoomed to center
PROP_ZOOM = 7  # the current zoom factor
PROP_TRANS_X = 8  # the current translation factor in x direction. 0 is normal 1 is the full image
PROP_TRANS_Y = 9  # the current translation factor in y direction
PROP_SHOW_MENU = 10  # True if the menu is shown


# the settings for the properties
# the view
STATE_OVERVIEW = 0
STATE_MAPVIEW = 1

STATE_NORMAL = 0
STATE_PREVIEW = 1  # preview state for the gm view state


class View(object):
    """A view holds the currently displayed image and has the functionality of displaying it and transforming.

    Depending on how the transformation will be handled in the future this class might be obsolete"""
    def __init__(self, img=np.zeros((5, 5, 3))):
        self.img = img.copy()  # the image that will be shown
        # this will also hold a transformation and the functions for transforming from and to a view

    def show(self, winname):
        """display the image in an cv2 window"""
        cv.imshow(winname, self.img)

    # this makes sure the image is copied
    def set_img(self, img):
        """set the image that is going to be shown"""
        self.img = img.copy()

    def coor_to_px(self, coor):
        """returns the pixel coor on the image transformed from the coor relative to the window"""
        print("view: coor_to_px(): THIS FUNCTION IS NOT PROPERLY DEFINED!!!")
        return coor


# displays the current game according to settings
class Viewer(object):
    """The viewer stores the properties that define how the map is going to be displayed and has functionality to render
    it"""
    def __init__(self, game):
        """save a reference to the game and set parameters

        :param game: The game of which the current map is going to be displayed
        """
        self.game = game

        # the states that decide how the map will be rendered
        self.states = {
            PROP_VIEW: STATE_MAPVIEW,
            PROP_MAP: 0,
            PROP_GRIDLINES: False,
            PROP_PLAYERS: True,
            PROP_UPDATE_MAIN: True,
            PROP_GM_VIEW: STATE_NORMAL,
            PROP_SHOW_TOKEN: True,
            PROP_ZOOM: 1,
            PROP_TRANS_X: 0,
            PROP_TRANS_Y: 0,
        }

        # create views
        self.main_view = View()
        self.gm_view = View()

        # create windows (for some reason cv.WINDOW_NORMAL. That should have to do with fullscreen)
        cv.namedWindow("main", cv.WINDOW_NORMAL)  # the main window on the TV
        cv.namedWindow("gm", cv.WINDOW_NORMAL)  # the secondary window for the gm

    def update(self):
        """the main update function governing what will be shown. A lot of the update function is defining the proper
        parameters to invoke the Map.get_image() function for the dm image and the main image"""

        if self.states[PROP_VIEW] == STATE_OVERVIEW:  # the worldmap
            if self.states[PROP_UPDATE_MAIN]:  # if the main view is being updated
                self.main_view.set_img(self.game.overview_map)  # set the view to the worldmap
            self.gm_view.set_img(self.game.overview_map_dm)  # set the view to the worldmap
        elif self.states[PROP_VIEW] == STATE_MAPVIEW:  # view a map
            # calculate zoom and translation parameters for the main_view
            params = {"fow": "tv"}  # the parameters that will be asked for in the image. fow will be a nice rendering
            if self.states[PROP_ZOOM] != 1:
                params["zoom"] = self.states[PROP_ZOOM]
            if self.states[PROP_TRANS_X]:
                params["trans_x"] = self.states[PROP_TRANS_X]
            if self.states[PROP_TRANS_Y]:
                params["trans_y"] = self.states[PROP_TRANS_Y]

            if self.states[PROP_SHOW_TOKEN]:
                params["tokens"] = True

            # only update main if allowed
            if self.states[PROP_UPDATE_MAIN]:
                self.main_view.set_img(self.game.curr_map().get_img(**params))

            # now that the main view is updated start changing the parameters to suit the gm view
            if self.states[PROP_UPDATE_MAIN]:
                params["border"] = True
            if self.states[PROP_GM_VIEW] == STATE_PREVIEW:  # preview is almost the image the main map shows + border
                self.gm_view.set_img(self.game.curr_map().get_img(**params))
            elif self.states[PROP_GM_VIEW] == STATE_NORMAL:  # normal gm view
                # add fow param for the gm's view
                if self.states[PROP_GRIDLINES]:
                    params["gridlines"] = True
                params["fow"] = "gm"
                params["dm"] = True
                params["tokens"] = True
                self.gm_view.set_img(self.game.curr_map().get_img(**params))  # get image and set view

        # actually show the images created
        self.gm_view.show("gm")
        self.main_view.show("main")

    # some functionality to change viewer properties ========================================
    def set_prop(self, state, prop):
        """sets a state to a new property and updates everything. Use this to change viewer properties"""
        if not state in self.states:
            print("no such state:", state)
            return
        self.states[state] = prop
        self.update()

    def get_prop(self, state):
        return self.states[state]

    def inv_prop(self, state):
        """inverts the state if state is boolean"""
        self.states[state] = not self.states[state]

    def increase_prop(self, state, amount):
        self.states[state] += amount

    def decrease_prop(self, state, amount):
        self.states[state] -= amount

    @staticmethod
    def toggle_fullscreen():
        """toggles fullscreen of the main window"""
        if cv.getWindowProperty("main", cv.WND_PROP_FULLSCREEN) == cv.WINDOW_FULLSCREEN:
            cv.setWindowProperty("main", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        else:
            cv.setWindowProperty("main", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def next_map(self):
        """display next map. clips to max"""
        self.states[PROP_MAP] += 1
        self.game.next_map()
        if self.states[PROP_MAP] >= len(self.game.maps):
            print("last map already")
            self.states[PROP_MAP] -= 1
            return
        self.update()

    def prev_map(self):
        """display previous map. clips to 0"""
        self.states[PROP_MAP] -= 1
        self.game.prev_map()
        if self.states[PROP_MAP] < 0:
            print("first map already")
            self.states[PROP_MAP] += 1
            return
        self.update()

    def trans_gm_main(self, x, y):
        """a try to translate coordinates from gm to main view. this is wrong!!!"""

        print("Viewer.trans_gm_main(): ERROR FUNCTION IS NOT PROPERLY DEFINED!")

        dmshape = self.gm_view.img.shape
        mainshape = self.main_view.img.shape
        s = self.states[PROP_ZOOM]
        tx = self.states[PROP_TRANS_X]
        ty = self.states[PROP_TRANS_Y]
        ox = dmshape[1]
        oy = dmshape[0]
        nx = mainshape[1]
        ny = mainshape[0]

        new_x = (x / s + tx * ox) / (ox / s) * nx
        new_y = (y / s + ty * oy) / (oy / s) * ny

        return new_x, new_y
