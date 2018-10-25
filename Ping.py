import cv2 as cv
import numpy as np
from DNDMapTool.ImProcessing import alpha_blend_nb


class Ping(object):
    """this object goes through a timed ping animation (wripple waves)"""
    def __init__(self, px, py, size=100, lifetime_s=2.5, speed_mul=1):
        """Define all parameters that describe the pings appearance

        :param px: x pos
        :param py: y pos
        :param size: the size of the rectangle in which the ping is contained
        :param lifetime_s: the time the ping will take to animate
        :param speed_mul:  a value determining the speed the waves travel at (no proper unit)
        """
        self.px = int(px)
        self.py = int(py)
        self.img = np.zeros((size, size, 3))  # the canvas of the animation
        self.time = 0  # the current time in the lifetime of the animation
        self.lifetime = lifetime_s * speed_mul
        self.speed_mul = speed_mul
        self.wripples = []  # stores the sizes of all wripples that will be displayed
        # the time between two wripples
        self.dw = 0.5
        self.growthrate = 100
        # this is true if a new wripple can be added
        self.new_wripple_time = 0


    # updates the image with one iteration
    def iter(self, dt):
        """Does an animation iteration

        :param dt: the time between the last iterations
        :return: False if dead else True
        """
        self.img[:, :, :] = 0  # clear image
        self.time += dt * self.speed_mul  # advance time
        if self.time > self.lifetime:  # return false because Dead
            return False
        else:
            if self.time > self.new_wripple_time:  # check if a new wripple should be added

                # add a new wripple and set time for the next addition of a wripple
                self.wripples.append(0)
                self.new_wripple_time = self.time + self.dw
            for i in range(len(self.wripples)):
                # grow and draw all wripples
                self.wripples[i] += dt * self.growthrate
                cv.circle(self.img, (self.img.shape[0] // 2, self.img.shape[1] // 2), int(self.wripples[i]), (255, 0, 0), 5)
            return True

    def blit(self, b_img):
        """blit self onto an image centered on self.px and self.py

        :param b_img: the image that is blittet onto
        :return: None
        """
        sx = self.img.shape[1]
        sy = self.img.shape[0]
        # half of size for center (size needs to be divisible by two or an error will br raised)
        dx = sx // 2
        dy = sy // 2

        # only blit where wripples have been drawn. This preserves the background and adds
        # transperancy without an alpha channel
        mask = self.img != 0
        b_img[self.py - dy:self.py + dy, self.px - dx:self.px + dx][mask] = self.img[mask]
