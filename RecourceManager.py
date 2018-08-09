import cv2 as cv
import numpy as np
import os
from DNDMapTool.Game import Game
from DNDMapTool.Map import Map
from DNDMapTool.Token import Token, descrip_type
import configparser as cfgp
import re


# loads image from path and converts it to a numpy array. this also has some extra functionality
def load_img(path, **kwargs):
    # this describes the action to the image. scaling is applied after rotation
    params = {
        "rotate": False,
        "f": 1,  # the homogeneous scale factor
    }
    if "filetype" in kwargs:
        filetype = kwargs["filetype"]
    else:
        filetype = ".jpg"
    if "load_alpha" in kwargs and kwargs["load_alpha"]:
        img = np.array(cv.imread(path + filetype, cv.IMREAD_UNCHANGED)).astype(np.uint8)
    else:
        img = np.array(cv.imread(path + filetype)).astype(np.uint8)
    # rotate the image so that the largest dimension is x (columns)
    if "autorotate" in kwargs and kwargs["autorotate"]:
        # rotate if y dim is greater then x dim
        if img.shape[0] > img.shape[1]:
            # rotate the image around color axes
            img = np.rot90(img)  # rotates ccw
            params["rotate"] = True
    # scales the image that it fits on the screen
    if "autoscale" in kwargs and kwargs["autoscale"]:
        fx = 1920 / img.shape[1]
        fy = 1080 / img.shape[0]
        # scale to the smaller factor
        f = min(fx, fy)
        img = cv.resize(img, (0, 0), fx=f, fy=f)
        params["f"] = f

    return img, params


def load_map(path, name):
    my_map = Map(name)
    config = cfgp.ConfigParser()
    config.read(path + "\\" + "config.ino")
    if "settings" in config:
        settings = dict(config["settings"])
        for k, v in settings.items():
            if k in my_map.__dict__.keys():
                if v.isdigit():
                    v = int(v)
                my_map.__dict__[k] = v
    img, params = load_img(path + "\\" + "Player", autorotate=True, autoscale=True)
    dm_img, _ = load_img(path + "\\" + "DM", autorotate=True, autoscale=True)
    my_map.dm_img = dm_img
    # the image was rotated by 90 degrees
    if params["rotate"]:
        # switch nx and ny
        my_map.nx, my_map.ny = my_map.ny, my_map.nx
        # rotate margins
        my_map.mxl, my_map.mxr, my_map.myt, my_map.myb = my_map.myt, my_map.myb, my_map.mxr, my_map.mxl
    if params["f"] != 1:
        f = params["f"]
        my_map.mxl = int(my_map.mxl * f)
        my_map.mxr = int(my_map.mxr * f)
        my_map.myt = int(my_map.myt * f)
        my_map.myb = int(my_map.myb * f)
    my_map.update_image(img)
    return my_map


def load_game(path, name):
    game_dir = path + "\\" + name
    game = Game(name, load_img(game_dir + "\\" + "MainMap", autorotate=True, autoscale=True)[0])
    game.overview_map_dm = load_img(game_dir + "\\" + "MainMapDm", autorotate=False, autoscale=True)[0]
    # for every subdirectory in order
    for x in os.walk(game_dir):
        if len(x[1]):
            for folder in x[1]:
                # check if beginning is a number
                matches = re.findall("^[0-9]+", folder)
                if len(matches):
                    game.maps.append(load_map(x[0] + "\\" + folder, re.sub("^[0-9]+_*", "", folder)))
    print(len(game.maps))
    return game


def load_tokens(path):
    tokens = []
    for x in os.walk(path):
        for file in x[2]:
            name = re.sub("\..*$", "", file)
            descriptors = {}
            for d in name.split("_"):
                if d.isdigit():
                    continue
                d_type = descrip_type(d)
                if d_type:
                    descriptors[d_type] = d.lower()
            img = load_img(path + "\\" + name, filetype=".png", load_alpha=True)[0]  #removes file ending and loads image
            token = Token(img[:, :, :3], img[:, :, 3], descriptors)
            tokens.append(token)
    return tokens


if __name__ == "__main__":
    path = r"Tokens"
    img = cv.resize(np.array(cv.imread("OldMap.jpg")), (1500, 700))
    tokens = load_tokens(path)
    tokens[0].blit(img, (400, 500), 100, 100)
    cv.imshow("test", img)


    cv.waitKey(0)
    cv.destroyAllWindows()

