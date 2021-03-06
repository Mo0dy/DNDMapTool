import cv2 as cv
import numpy as np
import numba as nb
import time

"""Image processiong functions. Some are updated and useful others are not. use with care"""

#

dirs = [np.array((1, 0)), np.array((0, 1)), np.array((-1, 0)), np.array((0, -1)), np.array((-1, -1)), np.array((1, 1)), np.array((1, -1)), np.array((-1, 1))]
# this will get a numpy array and return all connected color cells
def connected_regions(img, r_arr, coor, delta, old_color):
    if not r_arr[tuple(coor)]:
        # check distance
        diff = img[tuple(coor)].astype(int) - old_color.astype(int)
        if np.sqrt(diff @ diff) < delta:
            r_arr[tuple(coor)] = True
            for d in dirs:
                new_coor = d + coor
                if 0 <= new_coor[1] < img.shape[1] and 0 <= new_coor[0] < img.shape[0]:
                    connected_regions(img, r_arr, new_coor, delta, img[tuple(coor)])

@nb.jit
def con_reg_stack(img, r_arr, start_coor, delta):
    stack = [start_coor]

    while len(stack):
        coor = stack.pop()
        for d in dirs:
            n_coor = d + coor
            if not r_arr[tuple(n_coor)]:
                # check distance
                diff = img[tuple(coor)].astype(int) - img[tuple(n_coor)].astype(int)
                if np.sqrt(diff @ diff) < delta:
                # if np.abs(img[tuple(coor)] - img[tuple(n_coor)]) < delta:
                    r_arr[tuple(coor)] = True
                    stack.append(n_coor)


# find regions in edges
@nb.jit
def con_reg_edges(edges, r_arr, start_coor, inverse=False):
    stack = [start_coor]
    img = edges.astype(np.bool)

    while len(stack):
        coor = stack.pop()
        for d in dirs:
            n_coor = d + coor
            if 0 <= n_coor[1] < img.shape[1] and 0 <= n_coor[0] < img.shape[0]:
                if not r_arr[tuple(n_coor)]:
                    # check distance
                    if edges[tuple(n_coor)] == inverse:
                        r_arr[tuple(coor)] = True
                        stack.append(n_coor)


# blend F onto B unsing A as aplha
def alpha_blend(F, B, A):
    a = A / 255
    ret_arr = np.zeros(F.shape)
    ret_arr[:, :, 0] = a * F[:, :, 0] + (1 - a) * B[:, :, 0]
    ret_arr[:, :, 1] = a * F[:, :, 1] + (1 - a) * B[:, :, 1]
    ret_arr[:, :, 2] = a * F[:, :, 2] + (1 - a) * B[:, :, 2]
    return ret_arr.astype(np.uint8)


@nb.guvectorize([(nb.uint8[:, :, :], nb.uint8[:, :, :], nb.float64[:, :])], '(a,b,c),(a,b,c),(a,b)', target="parallel", fastmath=True)
def alpha_blend_nb(F, B, A):
    for i in range(F.shape[0]):
        for j in range(F.shape[1]):
            a = A[i, j] / 255
            for c in range(F.shape[2]):
                B[i, j, c] = a * F[i, j, c] + (1 - a) * B[i, j, c]


def alpha_blend_nb_general(F, B, A, px=0, py=0):
    """this function alphablends one image onto another. The images do not have to be the same size and can be
    translated using px and py

    :param F: the background
    :param B: the foreground
    :param A: alpha channel
    :param px: translation x
    :param py: translation y
    :return:
    """

    # this invokes alpha_blend_nb_backend for the actual blending but clips the arrays first to avoid indexing problems.
    if py >= B.shape[0] or px >= B.shape[1]:  # plausibility check (can't blit if you are completely off target)
        return

    # the min and max values of the area that will be blittet onto on B. They will be clipped to 0 and the max axis
    # length
    ymin = py
    ymax = py + F.shape[0]
    xmin = px
    xmax = px + F.shape[1]

    ymin_offset = 0
    ymax_offset = 0
    xmin_offset = 0
    xmax_offset = 0

    # calculate offsets for clipping F
    if ymin < 0:
        ymin_offset = abs(ymin)
        ymin = 0
    if ymax >= B.shape[0]:
        ymax_offset = ymax - B.shape[0]
        ymax = B.shape[0]
    if xmin < 0:
        xmin_offset = abs(xmin)
        xmin = 0
    if xmax >= B.shape[1]:
        xmax_offset = xmax - B.shape[1]
        xmax = B.shape[1]

    Fprime = F[ymin_offset:F.shape[0] - ymax_offset, xmin_offset: F.shape[1] - xmax_offset]
    Aprime = A[ymin_offset:A.shape[0] - ymax_offset, xmin_offset: A.shape[0] - xmax_offset]

    alpha_blend_nb(Fprime, B[ymin:ymax, xmin:xmax], Aprime)


@nb.guvectorize([(nb.uint8[:, :, :], nb.float64[:, :])], '(a,b,c),(a,b)', target="parallel", fastmath=True)
def darken_maks(B, A):
    for i in range(B.shape[0]):
        for j in range(B.shape[1]):
            if A[i, j]:
                for c in range(B.shape[2]):
                    B[i, j, c] = B[i, j, c] / 2


def edge_detect(img):
    blur = cv.GaussianBlur(cv.cvtColor(img, cv.COLOR_BGR2GRAY), (5, 5), 0)
    return cv.Canny(blur, 250, 255)


if __name__ == "__main__":
    path = r"C:\Users\felix\Google Drive\D&D\Maps\LostMineOfPhandelver\CragmawHideout.jpg"
    img = np.array(cv.imread(path))
    edges = edge_detect(img).astype(np.uint8)
    view_img = edges


    cv.imshow("image", img)
    r_arr = np.zeros(img.shape[:2]).astype(bool)

    lb_down = False

    def mouse_callback(event, x, y, param, flags):
        global lb_down, edges
        if event == cv.EVENT_RBUTTONDOWN:
            cv.destroyWindow("test")
            r_arr[:, :] = False
            # connected_regions(img, r_arr, np.array((y, x)), 20, img[(y, x)])
            # con_reg_stack(edges, r_arr, np.array((y, x)), 20)
            con_reg_edges(edges, r_arr, np.array((y, x)))
            print("done")
            view_img = r_arr.astype(np.uint8) * 255
            # view_img[r_arr] = (255, 0, 0)
            cv.imshow("image", view_img)
        elif event == cv.EVENT_LBUTTONDOWN:
            lb_down = True
        elif event == cv.EVENT_LBUTTONUP:
            lb_down = False

        if lb_down:
            edges[y, x] = 255
        area = 30
        zoom = 5
        zoom_img = cv.resize(edges[max(0, y - area):min(y + area, edges.shape[0] - 1), max(0, x - area): min(x + area, edges.shape[1] - 1)], (0, 0), fx=zoom, fy=zoom)
        half_y = zoom_img.shape[0] // 2
        half_x = zoom_img.shape[1] // 2
        zoom_img[half_y:half_y+1, :] = 100
        zoom_img[:, half_x:half_x+1] = 100
        cv.imshow("zoom", zoom_img)

    cv.setMouseCallback("image", mouse_callback)

    while True:
        k = cv.waitKey(10)
        if k == 27:
            break
        elif k == ord("r"):
            cv.imshow("image", edges)
        cv.imshow("image", view_img)
    cv.destroyAllWindows()