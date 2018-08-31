import cv2 as cv
from DNDMapTool.ImProcessing import alpha_blend_nb
import numpy as np
from copy import deepcopy


descriptors = {
    "race": ["human", "elv", "halfling", "dwarf"],
    "gender": ["male", "female"],
    "class": ["cleric", "wizard", "rogue", "fighter"],
}


# gets the correct descriptor type for a descriptor
def descrip_type(descrip):
    d = descrip.lower()
    for k, v in descriptors.items():
        if d in v:
            return k
    print("no such descriptor")
    return None


class Token(object):
    def __init__(self, sprite, alpha, descriptors, sx=100, sy=100):
        self.sprite = sprite.copy()
        self.alpha = alpha.copy()
        self.descriptors = descriptors  # the parameters defining the token as a dict i.e.: "gender": "male" etc.
        # the size in pixels
        self.sx = sx
        self.sy = sy

    def get_to_size(self, sx, sy):  # returns the sprite according to cell size:
        # if the cells are to small the peices are going to be bigger then the cells.
        # otherwise hold a margin
        # this should be a homogeneous scale!
        return cv.resize(self.sprite, (sy, sx)), cv.resize(self.alpha, (sy, sx))

    def blit(self, target, pos, sx, sy):
        sx = int(sx)
        sy = int(sy)
        if sx % 2:
            sx -= 1
        if sy % 2:
            sy -= 1
        source, alpha = self.get_to_size(sx, sy)
        dx = sx // 2
        dy = sy // 2
        alpha_blend_nb(source, target[pos[0]-dy:pos[0]+dy, pos[1]-dx:pos[1]+dx], alpha)

    def copy(self):
        return deepcopy(self)

    def zoom(self, zoom_fac):
        self.sx = int(self.sx * zoom_fac)
        self.sy = int(self.sy * zoom_fac)

    # returns an image with all the information about the entity
    def info_window(self):
        img = np.ones((50, 50, 3)).astype(np.uint8) * 100
        row = 10
        for type, d in self.descriptors.items():
            cv.addText(img, type + ": " + d, (row, 10), "ArialBlack", 5)
            row += 50
        return img
