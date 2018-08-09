import cv2 as cv
from DNDMapTool.RecourceManager import load_tokens


# this loads the tokens and allows you to browse through them
class TokenBrowser(object):
    def __init__(self):
        self.tokens = load_tokens("Tokens")

    def __del__(self):
        pass