import cv2 as cv
import numpy as np
from DNDMapTool.Map import Map
from DNDMapTool.Game import Game
from DNDMapTool.RecourceManager import load_game
from DNDMapTool import Viewer
import time

path = r"C:\Users\Felix\Google Drive\D&D\Stories"


game = load_game(path, "LostMineOfPhandelver")
viewer = Viewer.Viewer(game)
viewer.update()


mouse_x = 0
mouse_y = 0
pressed = set()
def mouse_callback(event, x, y, flags, param):
    global selected_field, mouse_x, mouse_y, connected_reg, mw_pressed
    mouse_x = x
    mouse_y = y
    if event == cv.EVENT_LBUTTONDOWN:
        pressed.add("lmb")
    elif event == cv.EVENT_RBUTTONDOWN:
        pressed.add("rmb")
    elif event == cv.EVENT_LBUTTONUP:
        pressed.remove("lmb")
    elif event == cv.EVENT_RBUTTONUP:
        pressed.remove("rmb")
    if "lmb" in pressed:
        game.curr_map().clear_fog(np.array((y, x)), 60)
        viewer.update()
    elif "rmb" in pressed:
        game.curr_map().add_fog(np.array((y, x)), 60)
        viewer.update()


def toggle_fullscreen():
    if cv.getWindowProperty("main_window", cv.WND_PROP_FULLSCREEN) == cv.WINDOW_FULLSCREEN:
        cv.setWindowProperty("main_window", cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
    else:
        cv.setWindowProperty("main_window", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)


cv.setMouseCallback("gm", mouse_callback)
while True:
    k = cv.waitKey(1)
    if k == 27:
        break
    elif k == ord("m"):
        if viewer.get_prop(Viewer.PROP_VIEW) == Viewer.STATE_OVERVIEW:
            viewer.set_prop(Viewer.PROP_VIEW, Viewer.STATE_MAPVIEW)
        else:
            viewer.set_prop(Viewer.PROP_VIEW, Viewer.STATE_OVERVIEW)
    elif k == ord("f"):
        toggle_fullscreen()
    elif k == ord("t"):
        # toggle gridlines
        viewer.inv_prop(Viewer.PROP_GRIDLINES)
    elif k == ord("p"):  # pause updating main view
        viewer.inv_prop(Viewer.PROP_UPDATE_MAIN)
        viewer.update()
    elif k == ord("o"):  # preview
        if viewer.get_prop(Viewer.PROP_GM_VIEW) == Viewer.STATE_PREVIEW:
            viewer.set_prop(Viewer.PROP_GM_VIEW, Viewer.STATE_NORMAL)
        else:
            viewer.set_prop(Viewer.PROP_GM_VIEW, Viewer.STATE_PREVIEW)


cv.destroyAllWindows()


