import cv2 as cv
import numpy as np
from DNDMapTool.Map import Map
from DNDMapTool.Game import Game
from DNDMapTool.RecourceManager import load_game
from DNDMapTool import Viewer
from DNDMapTool.TokenBrowser import TokenBrowser, token_win_name
from DNDMapTool.Ping import Ping
import time

path = r"C:\Users\Felix\Google Drive\D&D\Stories"


game = load_game(path, "LostMineOfPhandelver")
# game = load_game(path, "JungleOneShot")
token_b = TokenBrowser(game)
# game.maps[0].add_token(token_b.tokens[0], [200, 200])
viewer = Viewer.Viewer(game)
viewer.update()


# additional images that will be blitted onto the view window:
# tuples: (image, pos(x, y))
add_images = []
pings = []  # the pings that are currently being displayed

# for testing add a token to the first map
# game.maps[0].add_token(token_b.tokens[0], (5, 5))


# utility functions ==================================================================================================
# defines a bunch of functions and then maps them to keys
def toggle_overview_map():
    if viewer.get_prop(Viewer.PROP_VIEW) == Viewer.STATE_OVERVIEW:
        viewer.set_prop(Viewer.PROP_VIEW, Viewer.STATE_MAPVIEW)
    else:
        viewer.set_prop(Viewer.PROP_VIEW, Viewer.STATE_OVERVIEW)


def toggle_gridlines():
    viewer.inv_prop(Viewer.PROP_GRIDLINES)


def toggle_pause():
    viewer.inv_prop(Viewer.PROP_UPDATE_MAIN)
    viewer.update()


def toggle_preview():
    if viewer.get_prop(Viewer.PROP_GM_VIEW) == Viewer.STATE_PREVIEW:
        viewer.set_prop(Viewer.PROP_GM_VIEW, Viewer.STATE_NORMAL)
    else:
        viewer.set_prop(Viewer.PROP_GM_VIEW, Viewer.STATE_PREVIEW)


def toggle_fullscreen():
    viewer.toggle_fullscreen()


def next_map():
    viewer.next_map()


def prev_map():
    viewer.prev_map()


def toggle_show_tokens():
    viewer.inv_prop(Viewer.PROP_SHOW_TOKEN)
    viewer.update()


def zoom_in():  # zoom token if token is under mouse. else zoom image
    token = token_under_mouse()
    if token:
        token.zoom(1.25)
    else:
        viewer.set_prop(Viewer.PROP_ZOOM, viewer.get_prop(Viewer.PROP_ZOOM) * 1.25)
    viewer.update()


def zoom_out():
    token = token_under_mouse()  # zoom token if token is under mouse. else zoom image
    if token:
        token.zoom(0.75)
    else:
        viewer.set_prop(Viewer.PROP_ZOOM, viewer.get_prop(Viewer.PROP_ZOOM) * 0.75)


def trans_up():
    viewer.decrease_prop(Viewer.PROP_TRANS_Y, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    viewer.update()


def trans_down():
    viewer.increase_prop(Viewer.PROP_TRANS_Y, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    viewer.update()


def trans_right():
    viewer.increase_prop(Viewer.PROP_TRANS_X, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    viewer.update()


def trans_left():
    viewer.decrease_prop(Viewer.PROP_TRANS_X, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    viewer.update()


def clear_fog():
    game.curr_map().fog[:, :] = False
    viewer.update()


def add_fog():
    game.curr_map().fog[:, :] = True
    viewer.update()


def remove_token_or_reset():
    # check if token under mouse
    token = token_under_mouse()
    if token:
        game.curr_map().remove_token(token)
    else:
        viewer.set_prop(Viewer.PROP_ZOOM, 1)
        viewer.set_prop(Viewer.PROP_TRANS_Y, 0)
        viewer.set_prop(Viewer.PROP_TRANS_X, 0)


def show_info_window():
    token = game.curr_map().token_at(mx, my)
    if token:
        info = token.info_window()
        # draw information window():
        add_images.append((info, (mx, my)))


def ping():
    px, py = viewer.trans_gm_main(mx, my)
    pings.append(Ping(px, py))

# event functions =============================================================================================


#  the mouse callback for the token manager
def token_mouse_callback(event, x, y, flags, param):
    # call the mouse callback of the token manager returns true if changes are detected
    if token_b.mouse_callback(event, x, y, flags, param):
        viewer.update()  # update the viewer if changes have been made

# set mouse callback
cv.setMouseCallback(token_win_name, token_mouse_callback)


# store the mouse position if needed by other functions
mx = 0
my = 0
# store pressed mousebuttons for drag and drop
pressed = set()
move_token = None  # True if a token is currently being dragged


# returns the token under the current mouse position
def token_under_mouse():
    return game.curr_map().token_at(mx, my)


# the mouse callback function of the dm window
def mouse_callback(event, x, y, flags, param):
    global selected_field, mx, my, connected_reg, mw_pressed, move_token

    # store mouse position in global variables for other functions to access
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
    elif event == cv.EVENT_MBUTTONDOWN:  # if there is a token under the mouse drag and drop it
        # check if the current map has a token under mouse:
        token_at = token_under_mouse()
        if token_at:
            move_token = token_at
    elif event == cv.EVENT_MBUTTONUP:
        if move_token:  # if a token is being dragged drop it.
            token_at = token_under_mouse()
            if not token_at or token_at == move_token:  # free space to place
                game.curr_map().move_token(move_token, (my, mx))  # move the token
                viewer.update()
            move_token = None


# add the mouse callback function
cv.setMouseCallback("gm", mouse_callback)

# tracks ctrl key
button_modifier = False
last_time = 0  # time for dt calculation


# does the key handling. returns True if the "esc" key has been pressed
def handle_key(k):
    # this would be a way of cleanly handling functions that do multiple things depending on if a token is under the
    # mouse. it would allow a clean mapping of keys to functions.
    # def token_decorator(f1, f2):
    #     token = token_under_mouse()
    #     if token:
    #         f2(token)
    #     else:
    #         f1()




    # this dictionary maps the keys to the correct functions
    key_to_function = {
        ord("m"): toggle_overview_map,
        ord("p"): toggle_pause,
        ord("o"): toggle_overview_map,
        ord("f"): toggle_fullscreen,
        ord("x"): next_map,
        ord("z"): prev_map,
        ord("h"): toggle_show_tokens,
        ord("q"): zoom_in,
        ord("e"): zoom_out,
        ord("w"): trans_up,
        ord("s"): trans_down,
        ord("a"): trans_left,
        ord("d"): trans_right,
        ord("c"): clear_fog,
        ord("v"): add_fog,
        ord("r"): remove_token_or_reset,
        ord("i"): show_info_window,
        ord("u"): ping,
    }

    if k:
        # list all keys and their corresponding functions
        if k == ord("l"):
            print("=================================")
            for k, v in key_to_function.items():
                print(chr(k) + ":", v.__name__)
            print("=================================")
        elif k == 27:  # esc for leave
            return True  # true means break main loop
        else:
            #  run the associated function
            if k in key_to_function:
                key_to_function[k]()

    # old version with if statements
    # if k:
    #     if k == 27:
    #         return True
    #     elif k == ord("m"):
    #         if viewer.get_prop(Viewer.PROP_VIEW) == Viewer.STATE_OVERVIEW:
    #             viewer.set_prop(Viewer.PROP_VIEW, Viewer.STATE_MAPVIEW)
    #         else:
    #             viewer.set_prop(Viewer.PROP_VIEW, Viewer.STATE_OVERVIEW)
    #     elif k == ord("t"):
    #         # toggle gridlines
    #         viewer.inv_prop(Viewer.PROP_GRIDLINES)
    #     elif k == ord("p"):  # pause updating main view
    #         viewer.inv_prop(Viewer.PROP_UPDATE_MAIN)
    #         viewer.update()
    #     elif k == ord("o"):  # preview
    #         if viewer.get_prop(Viewer.PROP_GM_VIEW) == Viewer.STATE_PREVIEW:
    #             viewer.set_prop(Viewer.PROP_GM_VIEW, Viewer.STATE_NORMAL)
    #         else:
    #             viewer.set_prop(Viewer.PROP_GM_VIEW, Viewer.STATE_PREVIEW)
    #     elif k == ord("f"):  # toogle fullscreen
    #         viewer.toggle_fullscreen()
    #     elif k == ord("z"):
    #         viewer.prev_map()
    #     elif k == ord("x"):
    #         viewer.next_map()
    #     elif k == ord("s"):  # show tokens
    #         viewer.inv_prop(Viewer.PROP_SHOW_TOKEN)
    #         viewer.update()
    #     elif k == ord("e"):
    #         token = game.curr_map().token_at(mx, my)
    #         if token != None:
    #             token.zoom(1.25)
    #         else:
    #             viewer.set_prop(Viewer.PROP_ZOOM, viewer.get_prop(Viewer.PROP_ZOOM) * 1.25)
    #         viewer.update()
    #     elif k == ord("q"):
    #         token = game.curr_map().token_at(mx, my)
    #         if token != None:
    #             token.zoom(0.75)
    #         else:
    #             viewer.set_prop(Viewer.PROP_ZOOM, viewer.get_prop(Viewer.PROP_ZOOM) * 0.75)
    #         viewer.update()
    #     elif k == 56:  # up
    #         viewer.decrease_prop(Viewer.PROP_TRANS_Y, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    #         viewer.update()
    #     elif k == 54:  # right
    #         viewer.increase_prop(Viewer.PROP_TRANS_X, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    #         viewer.update()
    #     elif k == 50:  # down
    #         viewer.increase_prop(Viewer.PROP_TRANS_Y, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    #         viewer.update()
    #     elif k == 52:  # left
    #         viewer.decrease_prop(Viewer.PROP_TRANS_X, 0.1 / viewer.get_prop(Viewer.PROP_ZOOM))
    #         viewer.update()
    #     elif k == ord("u"):  # show complete map
    #         game.curr_map().fog[:, :] = False
    #         viewer.update()
    #     elif k == ord("r"):
    #         # check if token under mouse
    #         viewer.set_prop(Viewer.PROP_ZOOM, 1)
    #         viewer.set_prop(Viewer.PROP_TRANS_Y, 0)
    #         viewer.set_prop(Viewer.PROP_TRANS_X, 0)
    #         viewer.update()
    #     elif k == ord("y"):
    #         viewer.inv_prop(Viewer.PROP_SHOW_TOKEN)
    #         viewer.update()
    #     elif k == ord("i"):
    #         token = game.curr_map().token_at(mx, my)
    #         info = token.info_window()
    #         # draw information window():
    #         add_images.append((info, (mx, my)))
    #     elif k == ord("n"):
    #         px, py = viewer.trans_gm_main(mx, my)
    #         pings.append(Ping(px, py))
    #     elif k == ord("h"):
    #         token = game.curr_map().token_at(mx, my)
    #         if token != None:
    #             game.curr_map().remove_token(token)
    return False  # False means do not break main loop

# the main loop of the program
while True:
    # calculate dt
    dt = time.time() - last_time
    last_time = time.time()
    k = cv.waitKey(1)
    if handle_key(k):  # if True esc. has been pressed
        break

    # draw fog if pressed
    if "lmb" in pressed:
        game.curr_map().clear_fog(np.array((my, mx)), 60)
        viewer.update()
    elif "rmb" in pressed:
        game.curr_map().add_fog(np.array((my, mx)), 60)
        viewer.update()

    # add arrow:
    if move_token or len(add_images):
        n_img = viewer.gm_view.img.copy()

        for img, pos in add_images:
            n_img[pos[1]:pos[1] + img.shape[0], pos[0]:pos[0] + img.shape[0], :] = img

        if move_token:
            t_pos = game.curr_map().token_pos(move_token)
            cv.arrowedLine(viewer.gm_view.img, (t_pos[1], t_pos[0]), (mx, my), (255, 0, 0), 3)
        viewer.gm_view.show("gm")
        viewer.gm_view.set_img(n_img)

    if len(pings):
        n_img = viewer.main_view.img.copy()
        # update pings
        for ping in pings:
            if ping.iter(dt):
                ping.blit(viewer.main_view.img)
            else:
                del ping
        viewer.main_view.show("main")
        viewer.main_view.set_img(n_img)


cv.destroyAllWindows()


