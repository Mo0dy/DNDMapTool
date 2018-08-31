import cv2 as cv
from DNDMapTool.RecourceManager import load_tokens
import cv2 as cv
import numpy as np


token_win_name = "TokenBrowser"


# this loads the tokens and allows you to browse through them
class TokenBrowser(object):
    def __init__(self, game):
        self.tokens = load_tokens("Tokens")
        self.columns = 8
        self.view_img = self.create_view_img()
        cv.imshow(token_win_name, self.view_img)
        self.game = game

    def create_view_img(self):
        # create the view image with enough size to fit all tokens (self.columns per row)
        view_img = np.ones((100 * int(np.ceil(len(self.tokens) / self.columns)) + 2, 100 * self.columns + 2, 3)).astype(np.uint8) * 50

        for i, t in enumerate(self.tokens):
            # calculate the row and column the token would be at. First fill columns then next row
            column = i // self.columns
            row = i % self.columns
            # blit image at correct position
            t.blit(view_img, (column * 100 + 50, row * 100 + 50), 100, 100)

        return view_img

    def __del__(self):
        pass

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            # calculate what "square" (100, 100) the mouse is in and return the token (rows were filled first)
            column = x // 100
            row = y // 100

            token = row * self.columns + column

            self.game.curr_map().add_token(self.tokens[token].copy(), (100, 100))
            return True
        return False

