import cv2 as cv
import numpy as np
from ImProcessing import connected_regions as con_r

path = r"C:\Users\felix\Google Drive\D&D\Maps\LostMineOfPhandelver\CragmawHideout.jpg"
orig_img = np.array(cv.imread(path))
grid_x = 30
grid_y = 21

dx = orig_img.shape[1] / grid_x
dy = orig_img.shape[0] / grid_y

margin_x = 0
margin_y = 3

cv.namedWindow("window", cv.WND_PROP_FULLSCREEN)
cv.setWindowProperty("window", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)


players = [list(np.random.random_integers(2, 17, 2)) for _ in range(5)]


def draw_lines(img):
    for i in range(1, grid_x):
        line_x = int(i * dx) + margin_x
        img[:, max(0, line_x - 1): min(line_x + 1, img.shape[1] - 1), :] = 0
    for j in range(1, grid_y):
        line_y = int(j * dy) + margin_y
        img[max(0, line_y - 1): min(line_y + 1, img.shape[0] - 1), :, :] = 0
    return img


def draw_figures(img, pos_list):
    for p in pos_list:
        center_x = int((p[1] + 0.5) * dx) + margin_x
        center_y = int((p[0] + 0.5) * dy) + margin_y
        cv.circle(img, (center_x, center_y), int(min(dx, dy) / 2 - 5), (50, 50, 250), -1)


show_lines = True


def px_to_coor(x, y):
    # returns coor in j, i
    return [int(y // dy), int(x // dx)]


def coor_to_px_mid(coor):
    j, i = coor
    return int((i + 0.5) * dx) + margin_x, int((j + 0.5) * dy) + margin_y


mouse_x = 0
mouse_y = 0
selected_field = None
connected_reg = None
def mouse_callback(event, x, y, flags, param):
    global selected_field, mouse_x, mouse_y, connected_reg
    mouse_x = x
    mouse_y = y
    if event == cv.EVENT_LBUTTONDOWN:
        coors = px_to_coor(x, y)
        if coors in players:
            selected_field = coors
    elif event == cv.EVENT_LBUTTONUP:
        coors = px_to_coor(x, y)
        # moved the mouse while dragging
        if coors != selected_field:
            if selected_field in players and not coors in players:
                players[players.index(selected_field)] = coors
        selected_field = None
    elif event == cv.EVENT_RBUTTONDOWN:
        connected_reg = con_r(img, np.array((y, x)).astype(int), 10)


cv.setMouseCallback("window", mouse_callback)
while True:
    img = orig_img.copy()
    k = cv.waitKey(100)
    if k == 27:
        break
    elif k == 116:
        show_lines = not show_lines
    if np.any(connected_reg):
        # print(np.sum(connected_reg.astype(int)))
        img[connected_reg] = (255, 0, 0)
    if show_lines:
        draw_lines(img)
    if selected_field:
        coors = px_to_coor(mouse_x, mouse_y)
        if coors in players:
            color = (50, 50, 250)
        else:
            color = (50, 250, 250)
        cv.arrowedLine(img, coor_to_px_mid(selected_field), coor_to_px_mid(coors), color, 2, cv.LINE_AA)
    draw_figures(img, players)
    cv.imshow("window", img)

cv.destroyAllWindows()


