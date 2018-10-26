import cv2 as cv
from DNDMapTool.ImProcessing import alpha_blend_nb
import numpy as np
from copy import deepcopy

"""The token class and some utility"""


# these are used to sort the tokens in the future / display information on them
descriptors = {
    "race": ["human", "elv", "halfling", "dwarf"],
    "gender": ["male", "female"],
    "class": ["cleric", "wizard", "rogue", "fighter"],
}


def descrip_type(descrip):
    """gets the correct descriptor type for a descriptor

    :param descrip: the descriptor as string
    :return: the descriptor type or None if there isn't any
    """
    d = descrip.lower()
    for k, v in descriptors.items():
        if d in v:
            return k
    print("no such descriptor")
    return None


class Token(object):
    """A token is an image with a position that can be put on the map"""
    def __init__(self, sprite, alpha, descriptors, sx=100, sy=100):
        """Set parameters

        :param sprite: the image file of the token
        :param alpha: an alpha layer used to add transparency
        :param descriptors: classification of the token for searches
        :param sx: x size
        :param sy: y size
        """
        self.sprite = sprite.copy()
        self.alpha = alpha.copy()
        self.descriptors = descriptors  # the parameters defining the token as a dict i.e.: "gender": "male" etc.
        # the size in pixels
        self.sx = sx
        self.sy = sy

    def get_to_size(self, sx, sy):  # returns the sprite according to cell size:
        """Resize self.img to sx and sy

        :param sx: x size
        :param sy: y size
        :return: a resized version of self.img
        """
        # this should be a homogeneous scale!
        return cv.resize(self.sprite, (sy, sx)), cv.resize(self.alpha, (sy, sx))

    def blit(self, target, pos, sx, sy):
        """blits self.img with proper size onto a target image

        :param target: the target image
        :param pos: the position of the midpoint of the image
        :param sx: x size
        :param sy: y size
        :return:
        """

        # convert sizes to integers for indexing and make sure they are divisible by two
        sx = int(sx)
        sy = int(sy)
        if sx % 2:
            sx -= 1
        if sy % 2:
            sy -= 1

        # resize
        source, alpha = self.get_to_size(sx, sy)

        # blit onto image relative to px and py as a midpoint
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
        """returns an image of the info window for this Token"""

        # this does not work until now. Some problems with the font rendering
        # @Macky given that we need this at other places as well (menu etc.) there should probably be some functions
        # dedicated to rendering fonts in proper sizes onto images (resizing new lines etc.)
        img = np.ones((50, 50, 3)).astype(np.uint8) * 100
        row = 10
        for type, d in self.descriptors.items():
            # cv.addText(img, type + ": " + d, (row, 10), cv.FONT_HERSHEY_SIMPLEX, 5)
            cv.addText(img, "test", (row, 10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            row += 50
        return img
