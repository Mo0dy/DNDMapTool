import cv2 as cv
from DNDMapTool.RecourceManager import load_tokens
import cv2 as cv
import numpy as np


"""The token browser is used to display / select and sort the tokens for use"""


# the cv2 window name the token browser will be rendered onto.
# another option would be ot blit it into the main menu or append it to one of the sides (later addition maybe)
token_win_name = "TokenBrowser"


# this loads the tokens and allows you to browse through them
class TokenBrowser(object):
    """Token Browser object collects and gives access to the tokens"""
    def __init__(self, game):
        """Creates parameters

        :param game: the game this token browser is going to display / add tokens to
        """
        # load tokens from file
        self.tokens = load_tokens("Tokens")
        self.columns = 8  # the amount of columns the tokens will be sorted into for viewing

        # create the view image. At the moment this is only one image. this should be scrollable and redraw if sorted.
        # also when we allow inputting search information the inputs should be displayed here
        self.view_img = self.create_view_img()

        # show image. again this should be done repeatedly once more functionality has been added
        cv.imshow(token_win_name, self.view_img)
        self.game = game

    def create_view_img(self):
        """creates the image that is going to be displayed

        :return: the image rendered with all tokens
        """
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
        """Destructor (destroys the window)"""
        cv.destroyWindow(token_win_name)

    def mouse_callback(self, event, x, y, flags, param):
        """The mouse callback function should be called from the main function. This is done so that the main function
        can invoke the viewer.update() function to update the viewer if a token got added.

        This is subobtimal and should probably be changed in the future (maybe a global variable that tracks if the
        viewer needs to be updated.

        :param event:
        :param x:
        :param y:
        :param flags:
        :param param:
        :return: True if the viewer needs to be updated
        """

        if event == cv.EVENT_LBUTTONDOWN:
            # calculate what "square" (100, 100) the mouse is in and return the token (rows were filled first)
            column = x // 100
            row = y // 100

            # get row from token order. The ordering and receiving of the order should be put into their own functions
            # once sorting / scrolling is implemented
            token = row * self.columns + column

            # add token to map
            self.game.curr_map().add_token(self.tokens[token].copy(), (100, 100))
            return True
        return False

