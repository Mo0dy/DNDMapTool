import cv2 as cv
import numpy as np
from DNDMapTool.Map import Map
from DNDMapTool.Game import Game
from DNDMapTool.RecourceManager import load_game
from DNDMapTool import Viewer
from DNDMapTool.TokenBrowser import TokenBrowser
import time

path = r"C:\Users\Felix\Google Drive\D&D\Stories"


# token_b = TokenBrowser()
game = load_game(path, "LostMineOfPhandelver")
viewer = Viewer.Viewer(game)
viewer.update()


# for testing add a token to the first map
# game.maps[0].add_token(token_b.tokens[0], (5, 5))


mx = 0
my = 0
pressed = set()
move_token = None
def mouse_callback(event, x, y, flags, param):
    global selected_field, mx, my, connected_reg, mw_pressed, move_token
    mx = x
    my = y
    if event == cv.EVENT_LBUTTONDOWN:
        pressed.add("lmb")
    elif event == cv.EVENT_RBUTTONDOWN:
        pressed.add("rmb")
    elif event == cv.EVENT_LBUTTONUP:
        pressed.remove("lmb")
    elif event == cv.EVENT_RBUTTONUP:
        pressed.remove("rmb")
    elif event == cv.EVENT_MBUTTONDOWN:
        # check if the current map has a token under mouse:
        grid_pos = game.curr_map().px_to_coor(mx, my)
        token_at = game.curr_map().token_at(grid_pos)
        if token_at:
            move_token = token_at
    elif event == cv.EVENT_MBUTTONUP:
        if move_token:
            grid_pos = game.curr_map().px_to_coor(mx, my)
            token_at = game.curr_map().token_at(grid_pos)
            if token_at == None:  # free space to place
                game.curr_map().move_token(move_token, grid_pos)  # move the token
                viewer.update()
            move_token = None

# tracks ctrl key
button_modifier = False
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
    elif k == ord("f"):  # toogle fullscreen
        viewer.toggle_fullscreen()
    elif k == ord("z"):
        viewer.prev_map()
    elif k == ord("x"):
        viewer.next_map()
    elif k == ord("s"):  # show tokens
        viewer.inv_prop(Viewer.PROP_SHOW_TOKEN)
        viewer.update()
    elif k == ord("e"):
        viewer.set_prop(Viewer.PROP_ZOOM, viewer.get_prop(Viewer.PROP_ZOOM) * 1.25)
        viewer.update()
    elif k == ord("q"):
        viewer.set_prop(Viewer.PROP_ZOOM, viewer.get_prop(Viewer.PROP_ZOOM) * 0.75)
        viewer.update()
    elif k == 56:  # up
        viewer.decrease_prop(Viewer.PROP_TRANS_Y, 0.1)
        viewer.update()
    elif k == 54:  # right
        viewer.increase_prop(Viewer.PROP_TRANS_X, 0.1)
        viewer.update()
    elif k == 50:  # down
        viewer.increase_prop(Viewer.PROP_TRANS_Y, 0.1)
        viewer.update()
    elif k == 52:  # left
        viewer.decrease_prop(Viewer.PROP_TRANS_X, 0.1)
        viewer.update()
    elif k == ord("u"):  # show complete map
        game.curr_map().fog[:, :] = False
        viewer.update()
    elif k == ord("r"):
        viewer.set_prop(Viewer.PROP_ZOOM, 1)
        viewer.set_prop(Viewer.PROP_TRANS_Y, 0)
        viewer.set_prop(Viewer.PROP_TRANS_X, 0)
        viewer.update()
    # draw fog if pressed
    if "lmb" in pressed:
        game.curr_map().clear_fog(np.array((my, mx)), 60)
        viewer.update()
    elif "rmb" in pressed:
        game.curr_map().add_fog(np.array((my, mx)), 60)
        viewer.update()

cv.destroyAllWindows()


