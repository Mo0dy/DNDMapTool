import cv2 as cv
from DNDMapTool.Game import Game
import numpy as np


# the properties that can be changes
PROP_VIEW = 0  # the current view
PROP_MAP = 1  # the current map
PROP_GRIDLINES = 2  # show gridlines (boolean)
PROP_PLAYERS = 3  # show players
PROP_UPDATE_MAIN = 4  # should the main window be updated?
PROP_GM_VIEW = 5  # the current state of the gm view


# the settings for the properties
# the view
STATE_OVERVIEW = 0
STATE_MAPVIEW = 1

STATE_NORMAL = 0
STATE_PREVIEW = 1  # preview state for the gm view state


class View(object):
    def __init__(self, img=np.zeros((5, 5, 3))):
        self.img = img.copy()  # the image that will be shown
        # this will also hold a transformation and the functions for transforming from and to a view

    def show(self, winname):
        cv.imshow(winname, self.img)

    # this makes sure the image is copied
    def set_img(self, img):
        self.img = img.copy()

    # returns the pixel coor on the image transformed from the coor relative to the window
    def coor_to_px(self, coor):
        return coor


# displays the current game according to settings
class Viewer(object):
    def __init__(self, game):
        self.game = game
        self.states = {
            PROP_VIEW: STATE_MAPVIEW,
            PROP_MAP: 0,
            PROP_GRIDLINES: True,
            PROP_PLAYERS: True,
            PROP_UPDATE_MAIN: True,
            PROP_GM_VIEW: STATE_NORMAL
        }

        self.main_view = View()
        self.gm_view = View()

        cv.namedWindow("main", cv.WINDOW_NORMAL)  # the main window on the TV
        cv.namedWindow("gm", cv.WINDOW_NORMAL)  # the secondary window for the gm

    # the main update function governing what will be shown
    def update(self):
        if self.states[PROP_VIEW] == STATE_OVERVIEW:
            if self.states[PROP_UPDATE_MAIN]:
                self.main_view.set_img(self.game.overview_map)
            self.gm_view.set_img(self.game.overview_map_dm)
        elif self.states[PROP_VIEW] == STATE_MAPVIEW:
            params = {"fow": "tv"}  # the parameters that will be asked for in the image

            # only update main if allowed
            if self.states[PROP_UPDATE_MAIN]:
                self.main_view.set_img(self.game.curr_map().get_img(**params))

            if self.states[PROP_UPDATE_MAIN]:
                params["border"] = True
            if self.states[PROP_GM_VIEW] == STATE_PREVIEW:
                self.gm_view.set_img(self.game.curr_map().get_img(**params))
            elif self.states[PROP_GM_VIEW] == STATE_NORMAL:
                # add fow param for the gm's view
                if self.states[PROP_GRIDLINES]:
                    params["gridlines"] = True
                params["fow"] = "gm"
                params["dm"] = True
                self.gm_view.set_img(self.game.curr_map().get_img(**params))

        # actually show the images created
        self.gm_view.show("gm")
        self.main_view.show("main")

    # sets a state to a new property and updates everything
    def set_prop(self, state, prop):
        if not state in self.states:
            print("no such state:", state)
            return
        self.states[state] = prop
        self.update()

    def get_prop(self, state):
        return self.states[state]

    # inverts the state if boolean
    def inv_prop(self, state):
        self.states[state] = not self.states[state]

    def toggle_fullscreen(self):
        if cv.getWindowProperty("main", cv.WND_PROP_FULLSCREEN) == cv.WINDOW_FULLSCREEN:
            cv.setWindowProperty("main", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        else:
            cv.setWindowProperty("main", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def next_map(self):
        self.states[PROP_MAP] += 1
        self.game.next_map()
        if self.states[PROP_MAP] >= len(self.game.maps):
            print("last map already")
            self.states[PROP_MAP] -= 1
            return
        self.update()

    def prev_map(self):
        self.states[PROP_MAP] -= 1
        self.game.prev_map()
        if self.states[PROP_MAP] < 0:
            print("first map already")
            self.states[PROP_MAP] += 1
            return
        self.update()
