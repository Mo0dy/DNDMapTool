import cv2 as cv


bimg = cv.imread("Button.png")

class Button(object):
    def __init__(self, name="default", x_size=100, y_size=50):
        self.x_size = x_size
        self.y_size = y_size
        self.name = name
        self.img = bimg.copy()
        cv.putText(self.img, self.name, (5, self.y_size - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv.imshow("test", self.img)

    def render(self):
        return self.img


class Menu(object):
    def __init__(self):
        self.menu = {}

    def __getitem__(self, item):
        return self.menu[item]

    def render(self):
        pass

def t1():
    print("t1")

def t2():
    print("t2")

def t3():
    print("t3")

if __name__ == "__main__":
    m = Menu()

    def main_m():
        m.menu = {
            Button("t1"): t1,
            Button("t2"): t2,
            Button("sm1"): sub_m1,
        }

    def sub_m1():
        m.menu = {
            Button("t3"): t3,
            Button("mm"): main_m
        }

