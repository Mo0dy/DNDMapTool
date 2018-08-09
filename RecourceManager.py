import cv2 as cv
import numpy as np
import os
from DNDMapTool.Game import Game
from DNDMapTool.Map import Map
import configparser as cfgp
import re


def load_img(path, filetype='.jpg'):
    return np.array(cv.imread(path + filetype)).astype(np.uint8)


def load_map(path, name):
    my_map = Map(name)
    config = cfgp.ConfigParser()
    config.read(path + "\\" + "config.ino")
    settings = dict(config["settings"])
    for k, v in settings.items():
        if k in my_map.__dict__.keys():
            if v.isdigit():
                v = int(v)
            my_map.__dict__[k] = v
    my_map.update_image(load_img(path + "\\" + "map"))
    return my_map


def load_game(path, name):
    game_dir = path + "\\" + name
    game = Game(name, load_img(game_dir + "\\" + "MainMap"))
    # for every subdirectory in order
    for x in os.walk(game_dir):
        if len(x[1]):
            # check if beginning is a number
            matches = re.findall("^[0-9]+", x[1][0])
            if len(matches):
                game.maps.append(load_map(x[0] + "\\" + x[1][0], re.sub("^[0-9]+_*", "", x[1][0])))

    return game
