import cv2 as cv
from DNDMapTool.RecourceManager import load_tokens
import cv2 as cv
import numpy as np


token_win_name = "TokenBrowser"


# this loads the tokens and allows you to browse through them
class TokenBrowser(object):
    def __init__(self, game):
        self.tokens = load_tokens("Tokens")
        self.view_img = self.create_view_img()
        cv.imshow(token_win_name, self.view_img)
        self.game = game

    def create_view_img(self):
        view_img = np.ones((100 * len(self.tokens) + 2, 102, 3)).astype(np.uint8) * 50

        for i, t in enumerate(self.tokens):
            t.blit(view_img, (i * 100 + 50, 50), 100, 100)

        return view_img

    def __del__(self):
        pass

    def show(self):
        pass

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            token = y // 100

            self.game.curr_map().add_token(self.tokens[token].copy(), (100, 100))
            return True
        return False