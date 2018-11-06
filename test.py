import numpy as np
import cv2 as cv

testarr = np.zeros((255, 255, 3)).astype(np.uint8)
testarr[100:150, 100:150, 1] = 255

cv.imshow("testwindow", testarr)
cv.waitKey(0)


