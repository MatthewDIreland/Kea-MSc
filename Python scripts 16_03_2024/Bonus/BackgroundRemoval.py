from PIL import Image
import cv2
import numpy as np
from PIL import ImageEnhance
from PIL import ImageStat

import matplotlib.pyplot as plt
from skimage import data
from skimage import exposure
from skimage.exposure import match_histograms

import pydip as pydip
import diplib as dip

def compare_images(image1, image2, threshold, output_path, block_size):
    # Open the images and convert to LAB color space
    # img1 = Image.open(image1)
    # print("here")
    # Load an image that contains all possible colors.

    lab_1 = cv2.cvtColor(cv2.imread(image1), cv2.COLOR_BGR2LAB)
    # lab_2 = cv2.cvtColor(fred, cv2.COLOR_BGR2LAB)
    lab_2 = cv2.cvtColor(cv2.imread(image2), cv2.COLOR_BGR2LAB)
    
    if lab_1.size != lab_2.size:
        raise ValueError("Images must have the same dimensions")
   
    # Iterate down comparing two np arrays if one value is different enough than another write out pixels to the third image that is being generated. Other write out a black pixel to that image.
    for x in range(4, len(lab_1) - block_size - 4, block_size):
        for y in range(4, len(lab_1[x]) - block_size - 4, block_size):
            l1_sum = 0
            a1_sum = 0
            b1_sum = 0 
            l2_sum = 0
            a2_sum = 0
            b2_sum = 0
            for a in range(0, block_size):
                for b in range(0, block_size):
                    l1, a1, b1 = lab_1[x + a][y + b]
                    l2, a2, b2 = lab_2[x + a][y + b]
                    l1_sum += l1
                    l2_sum += l2
                    a1_sum += a1
                    a2_sum += a2
                    b1_sum += b1
                    b2_sum += b2
            average_diff = (abs(l1_sum - l2_sum) + abs(a1_sum - a2_sum) + abs(b1_sum - b2_sum)) / (block_size*block_size)
            if average_diff < threshold:
                for a in range(0, block_size):
                    for b in range(0, block_size):
                        lab_1[x + a, y + b] = (0, 127, 127)


    result_image = cv2.cvtColor(lab_1.astype(np.uint8), cv2.COLOR_LAB2BGR)
    #result_image = color.lab2bgr(lab_1, illuminant='D55')
    cv2.imwrite(output_path, result_image)

compare_images("F:\Background removal\IMG_0643.JPG", "F:\Background removal\IMG_0642.JPG", 25, "F://Background removal//The results.png", 8)
print("Done!")
