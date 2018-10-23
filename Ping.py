import cv2 as cv
import numpy as np
from DNDMapTool.ImProcessing import alpha_blend_nb

# this object goes through a timed ping animation (wripple waves)
class Ping(object):
    def __init__(self, px, py, size=100, lifetime_s=2.5, speed_mul=1):
        self.px = int(px)
        self.py = int(py)
        self.img = np.zeros((size, size, 3))
        self.time = 0
        self.lifetime = lifetime_s * speed_mul
        self.speed_mul = speed_mul
        self.wripples = []
        # the time between two wripples
        self.dw = 0.5
        self.growthrate = 100
        # this is true if a new wripple can be added
        self.new_wripple_time = 0


    # updates the image with one iteration
    def iter(self, dt):
        self.img[:, :, :] = 0
        self.time += dt * self.speed_mul
        if self.time > self.lifetime:
            return False
        else:
            if self.time > self.new_wripple_time:
                self.wripples.append(0)
                self.new_wripple_time = self.time + self.dw
            for i in range(len(self.wripples)):
                self.wripples[i] += dt * self.growthrate
                cv.circle(self.img, (self.img.shape[0] // 2, self.img.shape[1] // 2), int(self.wripples[i]), (255, 0, 0), 5)
            return True

    def blit(self, b_img):
        sx = self.img.shape[1]
        sy = self.img.shape[0]
        dx = sx // 2
        dy = sy // 2
        mask = self.img != 0
        b_img[self.py - dy:self.py + dy, self.px - dx:self.px + dx][mask] = self.img[mask]



