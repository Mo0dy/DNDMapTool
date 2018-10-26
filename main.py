import cv2 as cv
import numpy as np
from DNDMapTool.Map import Map
from DNDMapTool.Game import Game
from DNDMapTool.RecourceManager import load_game
from DNDMapTool import Viewer
from DNDMapTool.TokenBrowser import TokenBrowser, token_win_name
from DNDMapTool.Ping import Ping
import time
from DNDMapTool.Menu import Menu, Button

"""The entrypoint for the program"""

# general notes:
# there should be a state system tracking the states of the program.
# at the moment all states are different independent variables such as:
# move_token
# pressed etc.
# this could also include main menu / normal program stuff or that the next mouse click has some special meaning e.g.
# select the resize function in the menu and then click the token that is going to be resized
#
# we should also have a better key handler in place as well as an event system
#
# we should find a way to query inputs e.g.: input name: "thomas". This means we would have to track if an input is
# being queried and then isolate the keystrokes until [enter] is pressed. (State system)


path = r"C:\Users\Felix\Google Drive\D&D\Stories"  # the path of the gamefiles that will be read
# load the maps and add. information of this game. In the future this
# could be input or done via a file manager
game = load_game(path, "LostMineOfPhandelver")
token_b = TokenBrowser(game)  # create a new token browser. this also loads all available tokens
viewer = Viewer.Viewer(game)  # create a new viewer. the viewer will render the map images according to properties
# updating the viewer shows the images (the show routine should probably be separate or the post
# processing should be added to the viewer
viewer.update()


# additional images that will be blitted onto the view window (post processing):
# tuples: (image, pos(x, y))
add_images = []
pings = []  # the pings that are currently being displayed

# the brushsize for the drawing of the fog
brushsize = 60
selected_rangefinder = None  # used if a rangefinder is supposed to be resized


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
    Viewer.Viewer.toggle_fullscreen()


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
    viewer.update()


def show_info_window():
    token = game.curr_map().token_at(mx, my)
    if token:
        info = token.info_window()
        # draw information window():
        add_images.append((info, (mx, my)))


def ping():
    px, py = viewer.trans_gm_main(mx, my)
    pings.append(Ping(px, py))


def fine_brush():
    global brushsize
    brushsize = 20


def normal_brush():
    global brushsize
    brushsize = 60


def coarse_brush():
    global brushsize
    brushsize = 200


def select_rangefinder():
    """Calls the scale rangefinder menu to scale a rangefinder selected rangefinder to a certain size"""
    global selected_rangefinder
    token = token_under_mouse()
    if "add" in token.descriptors and token.descriptors["add"] == "rangefinder":
        ranges_menu()
        selected_rangefinder = token


def set_range(range):
    """Sets the size of a rangefinder to a certain range (radius etc.) depending on the scale and its properties

    :param range: range in feet
    :return:
    """
    # get scale information from the current map
    x_pxper5feet = game.curr_map().x_pxper5feet
    y_pxper5feet = game.curr_map().y_pxper5feet

    if not (x_pxper5feet and y_pxper5feet):
        print("set_range: ERROR NO SCALE INFORMATION FOR THIS MAP")
        return

    # calculate pixlesize:
    pxx = int(x_pxper5feet / 5 * range)
    pxy = int(x_pxper5feet / 5 * range)

    if selected_rangefinder:
        selected_rangefinder.sx = pxx
        selected_rangefinder.sy = pxy
    else:
        print("set_range: ERROR NO RANGEFINDER SELECTED")


# build menu ==================================================================================================
menu = Menu()  # create a new menu


# create the functions for every submenu
# they have to populate the menu.menu dictionary with buttons and functions and assign positions to the buttons
# menu.update() automatically assignes positions to buttons
def main_menu():
    menu.menu = {
        Button("edit"): edit_menu,
        Button("view"): view_menu,
        Button("settings"): settings_menu,
    }
    menu.update()


def edit_menu():
    menu.menu = {
        Button("Next Map"): next_map,
        Button("Prev Map"): prev_map,
        Button("Add Fog"): add_fog,
        Button("Clear Fog"): clear_fog,
        Button("Brushsize"): brush_menu,
        Button("return"): main_menu,
    }
    menu.update()


def brush_menu():
    """select brushsize"""
    menu.menu = {
        Button("Fine"): fine_brush,
        Button("Normal"): normal_brush,
        Button("Coarse"): coarse_brush,
        Button("Return"): edit_menu,
    }
    menu.update()


def view_menu():
    menu.menu = {
        Button("Map"): toggle_overview_map,
        Button("Pause"): toggle_pause,
        Button("Show Tokens"): toggle_show_tokens,
        Button("Translations"): translation_menu,
        Button("Preview"): toggle_preview,
        Button("Return"): main_menu,
    }
    menu.update()


def translation_menu():
    # first create the buttons
    bup = Button("Up")
    bdown = Button("Down")
    bright = Button("Right")
    bleft = Button("Left")
    bzoom_in = Button("Zoom in")
    bzoom_out = Button("Zoom out")
    breturn = Button("Return")
    breset = Button("Reset")

    # assign the buttons to functions
    menu.menu = {
        bup: trans_up,
        bdown: trans_down,
        bright: trans_right,
        bleft: trans_left,
        bzoom_in: zoom_in,
        bzoom_out: zoom_out,
        breset: remove_token_or_reset,
        breturn: view_menu,
    }
    menu.update()  #autosort the position of the buttons

    # add custom positions to the buttons
    margin = 10
    x_size = bup.x_size
    y_size = bup.y_size

    row1 = margin
    row2 = margin * 2 + y_size
    row3 = margin * 3 + y_size * 2
    row4 = margin * 4 + y_size * 3

    column1 = margin
    column2 = margin * 2 + x_size
    column3 = margin * 3 + x_size * 2

    bup.x, bup.y = column2, row1
    bdown.x, bdown.y = column2, row2
    bleft.x, bleft.y = column1, row2
    bright.x, bright.y = column3, row2
    bzoom_in.x, bzoom_in.y = column3, row1
    bzoom_out.x, bzoom_out.y = column1, row1
    breset.x, breset.y = column1, row3
    breturn.x, breturn.y = column1, row4


def settings_menu():
    menu.menu = {
        Button("Fullscreen"): toggle_fullscreen,
        Button("Return"): main_menu,
    }
    menu.update()


def ranges_menu():
    def r1():
        set_range(20)
        main_menu()
        viewer.update()

    def r2():
        set_range(60)
        main_menu()
        viewer.update()

    def r3():
        set_range(120)
        main_menu()
        viewer.update()

    menu.menu = {
        Button("R10"): r1,
        Button("R30"): r2,
        Button("R60"): r3,
        Button("Return"): main_menu,
    }
    menu.update()


# start the first menu
main_menu()


# event functions =============================================================================================
def token_mouse_callback(event, x, y, flags, param):
    """the mouse callback for the token manager"""
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


def token_under_mouse():
    """returns the token under the current mouse position or None if there isn't any"""
    return game.curr_map().token_at(mx, my)


def mouse_callback(event, x, y, flags, param):
    """the mouse callback function of the dm window"""
    global mx, my, move_token

    # store mouse position in global variables for other functions to access
    mx = x
    my = y

    # event holds the current mouse events
    if event == cv.EVENT_LBUTTONDOWN:
        # check if cursor is on menu. else add to pressed buttons
        if not menu.click(x, y):  # click checks if the cursor clicks on a menu button and calls the associated function
            pressed.add("lmb")
    elif event == cv.EVENT_RBUTTONDOWN:
        pressed.add("rmb")
    elif event == cv.EVENT_LBUTTONUP:
        if "lmb" in pressed:
            pressed.remove("lmb")
    elif event == cv.EVENT_RBUTTONUP:
        if "rmb" in pressed:
            pressed.remove("rmb")
    elif event == cv.EVENT_MBUTTONDOWN:  # if there is a token under the mouse drag and drop it
        # check if the current map has a token under mouse:
        token_at = token_under_mouse()
        if token_at:
            move_token = token_at
    elif event == cv.EVENT_MBUTTONUP:
        if move_token:  # if a token is being dragged drop it.
            token_at = token_under_mouse()

            # check if the space is free to place the token
            # this should be a proper (rectangular / sprite) collision check.
            # also there should be a token property that decides if collision is going to take place on a per token
            # basis. This would allow the rangefinder tokens to blit over normal tokens.
            # There should also be an order in which the tokens get blitted and functionality to change that order
            # e.g. foreground background etc.
            if not token_at or token_at == move_token:
                game.curr_map().move_token(move_token, (my, mx))  # move the token
                viewer.update()
            move_token = None


# add the mouse callback function
cv.setMouseCallback("gm", mouse_callback)


last_time = 0  # time for dt calculation


def handle_key(k):
    """Does the key handling. returns True if the "esc" key has been pressed"""
    # this would be a way of cleanly handling functions that do multiple things depending on if a token is under the
    # mouse. it would allow a clean mapping of keys to functions.
    # def token_decorator(f1, f2):
    #     token = token_under_mouse()
    #     if token:
    #         f2(token)
    #     else:
    #         f1()

    # this dictionary maps the keys to the correct functions. this is where you can change keybindings (maybe we should
    # have a menu function to overwrite these and store and load them from a settings file)
    key_to_function = {
        ord("m"): toggle_overview_map,
        ord("p"): toggle_pause,
        ord("o"): toggle_preview,
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
        ord("b"): select_rangefinder,
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
    return False  # False means do not break main loop


# the main loop of the program ===========================================================
while True:
    # calculate dt
    dt = time.time() - last_time
    last_time = time.time()

    # read key with delay to draw everything
    k = cv.waitKey(1)

    if handle_key(k):  # True means esc. has been pressed
        break  # exit the program

    # draw fog if pressed
    if "lmb" in pressed:
        game.curr_map().clear_fog(np.array((my, mx)), brushsize)  # the clear fog functions clears a circle of fog
        viewer.update()
    elif "rmb" in pressed:  # add fog again
        game.curr_map().add_fog(np.array((my, mx)), brushsize)
        viewer.update()

    # post processing on the different images e.g. pings, arrows, menu etc. ===========================================
    # copy image to restore later. so that the next post processing can start
    # with a clean image even if the viewer does not get updates in the mean time

    # gm view =================================================================
    # at the moment the menu gets redrawn with every frame. this could be changed.

    n_img = viewer.gm_view.img.copy()  # this should only happen if postprocessing is going to happen for sure

    if move_token or len(add_images):  # blit the token that is being moved and all add. images
        for img, pos in add_images:
            viewer.gm_view.img[pos[1]:pos[1] + img.shape[0], pos[0]:pos[0] + img.shape[0], :] = img

        if move_token:
            t_pos = game.curr_map().token_pos(move_token)
            cv.arrowedLine(viewer.gm_view.img, (t_pos[1], t_pos[0]), (mx, my), (255, 0, 0), 3)
    # render menu
    menu.render(viewer.gm_view.img)
    # show gm view image and restore old image

    viewer.gm_view.show("gm")
    viewer.gm_view.set_img(n_img)

    # main view ===========================================================
    if len(pings):  # render all pings
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
