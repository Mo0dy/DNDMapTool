import cv2 as cv
import numpy as np

bimg = cv.imread("Button.png")  # the image for the button (maybe I should add a second hover or pressed one)


class Button(object):
    """a button has a position and a size and an image that can be rendered. It also can check for rectangular collision
    """
    def __init__(self, name="default", x_size=100, y_size=50):
        self.x_size = x_size
        self.y_size = y_size
        self.x = 0
        self.y = 0
        self.name = name
        self.img = bimg.copy()
        # render the name onto the button (this should probably have different font sizes according to line length)
        # another option would be making custom button images and load them from the names
        cv.putText(self.img, self.name, (5, self.y_size - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    def is_colliding(self, x, y):
        """checks if the point is colliding with the box of the button"""
        return self.x <= x <= self.x + self.x_size and self.y <= y <= self.y + self.y_size


class Menu(object):
    """the main menu has a position, a menu dictionary that holds the current options and can render / sort buttons

    To actually change the menu a function needs to be assigned to a button that directly modifies the self.menu
    contents. Look at the example below."""
    def __init__(self):
        # the position to render self
        self.x = 0
        self.y = 0
        self.menu = {}

    def __getitem__(self, item):
        return self.menu[item]

    def update(self):
        """assigns positions to all buttons"""
        y = 10
        margin = 10
        # set the x and y positions of the buttons relative to the menu
        for k, v in self.menu.items():
            k.y = y
            k.x = margin
            y += margin + k.y_size

    def click(self, x, y):
        """if the x and y position is on a button run that funtion.

        :param x: px x pos
        :param y: px y pos
        :return: True if button was clicked. otherwise return False
        """
        for k, b in self.menu.items():
            if k.is_colliding(x - self.x, y - self.y):
                b()
                return True
        return False

    def render(self, img):
        """renders the menu onto the image

        :param img: the image that the menu should be rendered onto
        :return: None
        """
        for k, v in self.menu.items():
            b_img = k.img
            img[self.y + k.y: self.y + k.y + k.img.shape[0], self.x + k.x: self.x + k.x + k.img.shape[1], :] = b_img[:, :, :]


if __name__ == "__main__":
    def t1():
        print("t1")


    def t2():
        print("t2")


    def t3():
        print("t3")


    m = Menu()

    def main_m():
        m.menu = {
            Button("t1"): t1,
            Button("t2"): t2,
            Button("sm1"): sub_m1,
        }
        m.update()

    def sub_m1():
        m.menu = {
            Button("t3"): t3,
            Button("mm"): main_m
        }
        m.update()

    main_m()


    #  the mouse callback for the token manager
    def token_mouse_callback(event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            m.click(x, y)


    # set mouse callback
    cv.setMouseCallback("test", token_mouse_callback)

    while True:
        t_img = np.ones((700, 300, 3)).astype(np.uint8) * 50
        m.render(t_img)
        cv.imshow("test", t_img)
        cv.waitKey(10)