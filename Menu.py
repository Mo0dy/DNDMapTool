import cv2 as cv
import numpy as np

bimg = cv.imread("Button.png")

class Button(object):
    def __init__(self, name="default", x_size=100, y_size=50):
        self.x_size = x_size
        self.y_size = y_size
        self.x = 0
        self.y = 0
        self.name = name
        self.img = bimg.copy()
        cv.putText(self.img, self.name, (5, self.y_size - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # checks if the point is colliding with the box of the button
    def is_colliding(self, x, y):
        return self.x <= x <= self.x + self.x_size and self.y <= y <= self.y + self.y_size


class Menu(object):
    def __init__(self):
        # the position to render self
        self.x = 0
        self.y = 0
        self.menu = {}

    def __getitem__(self, item):
        return self.menu[item]

    def update(self):
        # sorts the buttons
        y = 10
        margin = 10
        # set the x and y positions of the buttons relative to the menu
        for k, v in self.menu.items():
            k.y = y
            k.x = margin
            y += margin + k.y_size

    # returns true if a button was clicked
    def click(self, x, y):
        for k, b in self.menu.items():
            if k.is_colliding(x, y):
                b()
                return True
        return False

    def render(self, img):
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