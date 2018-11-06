import cv2 as cv
import numpy as np
import os
from DNDMapTool.Game import Game
from DNDMapTool.Map import Map
from DNDMapTool.Token import Token, descrip_type
import configparser as cfgp
import re

"""loads stuff from files"""
# Note: often there are multiple arguments that will get combined to a name such as: path + name + filending
# this should probably changed to just one path as this would make things much more straight forward


load_img_filetype = ".jpg"


def load_img(path, **kwargs):
    """loads image from path and converts it to a numpy array. this also has some extra functionality

    :param path: the parth the image will be loaded from
    :param kwargs: additional options such as filetype (if not jpg) or if to load an alpha channel as well
    :return: img, params: the loaded image and some parameters describing how it was changed from the original
    """
    # this describes the action to the image. scaling is applied after rotation
    params = {
        "rotate": False,
        "f": 1,  # the homogeneous scale factor
    }
    if "filetype" in kwargs:
        filetype = kwargs["filetype"]
    else:
        filetype = load_img_filetype
    if "load_alpha" in kwargs and kwargs["load_alpha"]:  # also loads alpha channel
        load_img = cv.imread(path + filetype, cv.IMREAD_UNCHANGED)
    else:
        load_img = cv.imread(path + filetype)
    if np.any(load_img):
        img = np.array(load_img).astype(np.uint8)
    else:
        print("could not load: " + path)
        return None, None

    # rotate the image so that the largest dimension is x (columns). this is so that the tv this is displayed on will
    # be used to display the image as large as it can
    if "autorotate" in kwargs and kwargs["autorotate"]:
        # rotate if y dim is greater then x dim
        if img.shape[0] > img.shape[1]:
            # rotate the image around color axes
            img = np.rot90(img)  # rotates ccw
            params["rotate"] = True

    # scales the image to full hd. (mostly only used for the dm image the map images should stay full size for zooming)
    if "autoscale" in kwargs and kwargs["autoscale"]:
        fx = 1920 / img.shape[1]
        fy = 1080 / img.shape[0]
        # scale to the smaller factor
        f = min(fx, fy)
        img = cv.resize(img, (0, 0), fx=f, fy=f)
        params["f"] = f

    return img, params


def load_map(path, name):
    """load the map images, properties and combine them to a map object

    :param path: the path to the folder the map is located in
    :param name: the name of the Map
    :return: the loaded Map
    """

    my_map = Map(name)

    # use ConfigParser to load the config file
    config = cfgp.ConfigParser()
    config.read(path + "\\" + "config.ino")
    if "settings" in config:
        settings = dict(config["settings"])

        # for every setting that has a matching variable in the Map object set that variable to the current setting
        for k, v in settings.items():
            if k in my_map.__dict__.keys():
                if v.isdigit():  # this should probably also allow for float values
                    v = int(v)
                my_map.__dict__[k] = v

    # load images
    img, params = load_img(path + "\\" + "Player", autorotate=True, autoscale=False)
    dm_img, _ = load_img(path + "\\" + "DM", autorotate=True, autoscale=True)

    # if there is no dm_image create one from the map image
    if not np.any(dm_img):
        # these could be put directly into the resize function
        fx = 1920 / img.shape[1]
        fy = 1080 / img.shape[0]
        # scale to the smaller factor
        f = min(fx, fy)
        dm_img = cv.resize(img, (0, 0), fx=f, fy=f)
    my_map.dm_img = dm_img

    # if the image was rotated by 90 degrees rotate all loaded parameters as well
    if params["rotate"]:
        # switch nx and ny
        my_map.nx, my_map.ny = my_map.ny, my_map.nx
        # rotate margins
        my_map.mxl, my_map.mxr, my_map.myt, my_map.myb = my_map.myt, my_map.myb, my_map.mxr, my_map.mxl

    # if the image was scaled: scale all parameters as well
    if params["f"] != 1:
        f = params["f"]
        my_map.mxl = int(my_map.mxl * f)
        my_map.mxr = int(my_map.mxr * f)
        my_map.myt = int(my_map.myt * f)
        my_map.myb = int(my_map.myb * f)

    my_map.update_image(img)  # this updates all settings and creates fow etc. for the image
    print("loaded map: ", name)
    return my_map


def load_game(path, name):
    """build and return a game object from a folder structure

    :param path: the path to the folder game folder is located in
    :param name: the name of the folder the files are located in
    :return: Game object loaded with all files from the path
    """

    # create path
    game_dir = path + "\\" + name
    # create game object. also pass the main overview map here
    game = Game(name, load_img(game_dir + "\\" + "MainMap", autorotate=True, autoscale=True)[0])
    # if applicable load an overview map for the dm
    game.overview_map_dm = load_img(game_dir + "\\" + "MainMapDm", autorotate=False, autoscale=True)[0]

    # for every subdirectory in order
    for x in os.walk(game_dir):
        if len(x[1]):
            for folder in x[1]:
                # check if beginning is a number. the way this interacts with the code after this might be buggy
                # if there are other numbers in the folder name
                matches = re.findall("^[0-9]+", folder)
                if len(matches):
                    # load the map out of the subfolder if ther is a "_" after the number
                    game.maps.append(load_map(x[0] + "\\" + folder, re.sub("^[0-9]+_*", "", folder)))
    print("loaded game. amount of maps:", len(game.maps))
    return game


def load_tokens(path):
    """Load all tokens from the path
    This also loads the descriptors from the token names

    :param path: the path the tokens are in
    :return: a list with all loaded tokens
    """
    tokens = []
    for x in os.walk(path):
        for file in x[2]:
            name = re.sub("\..*$", "", file)
            descriptors = {}
            for d in name.split("_"):
                if d.isdigit():
                    continue
                d_type = descrip_type(d)  # check what type the descriptor would be
                if d_type:
                    descriptors[d_type] = d.lower()  # add the descriptor
            # removes file ending and loads image
            img = load_img(path + "\\" + name, filetype=".png", load_alpha=True)[0]
            # create token with image, alpha and descriptors
            # theoretically alpha could stay in the image
            token = Token(img[:, :, :3], img[:, :, 3], descriptors)
            tokens.append(token)
    print("loaded", len(tokens), "tokens")
    return tokens


if __name__ == "__main__":
    path = r"Tokens"
    img = cv.resize(np.array(cv.imread("OldMap.jpg")), (1500, 700))
    tokens = load_tokens(path)
    tokens[0].blit(img, (400, 500), 100, 100)
    cv.imshow("test", img)


    cv.waitKey(0)
    cv.destroyAllWindows()

