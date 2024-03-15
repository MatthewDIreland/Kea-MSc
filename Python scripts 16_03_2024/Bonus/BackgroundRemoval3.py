import numpy as np 
import matplotlib.pyplot as plt 
import sys
from skimage.color import rgb2gray
import numpy as np
import cv2
from scipy import ndimage

image = plt.imread("F://Background removal//IMG_0837.JPG")
plt.imshow(image)

# converting to grayscale
gray = rgb2gray(image)

# defining the sobel filters
sobel_horizontal = np.array([np.array([1, 2, 1]), np.array([0, 0, 0]), np.array([-1, -2, -1])])
print(sobel_horizontal, 'is a kernel for detecting horizontal edges')
 
sobel_vertical = np.array([np.array([-1, 0, 1]), np.array([-2, 0, 2]), np.array([-1, 0, 1])])
print(sobel_vertical, 'is a kernel for detecting vertical edges')

out_h = ndimage.convolve(gray, sobel_horizontal, mode='reflect')
out_v = ndimage.convolve(gray, sobel_vertical, mode='reflect')

kernel_laplace = np.array([np.array([1, 1, 1]), np.array([1, -8, 1]), np.array([1, 1, 1])])
print(kernel_laplace, 'is a laplacian kernel')

out_l = ndimage.convolve(gray, kernel_laplace, mode='reflect')
# plt.imshow(out_l, cmap='gray')
cv2.imwrite("F://Background removal//output1.png", out_l)
print("dossne")

# here mode determines how the input array is extended when the filter overlaps a border.
# # Loading required libraries

# file1_path = sys.argv[1]
# file2_path = sys.argv[2]
# groups = int(sys.argv[3])

# import matplotlib.pyplot as plt
# from skimage import data
# from skimage import exposure
# from skimage.exposure import match_histograms
# import numpy as np


# # load image from images directory
# image = cv2.imread(file1_path)
# # Change color to RGB (from BGR)
# image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
# # Reshaping the image into a 2D array of pixels and 3 color values (RGB) 
# pixel_vals = image.reshape((-1,3)) # numpy reshape operation -1 unspecified 
# # Convert to float type only for supporting cv2.kmean
# pixel_vals = np.float32(pixel_vals)
# #criteria
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85) 
# # Choosing number of clusters
# k = groups

# retval, labels, centers = cv2.kmeans(pixel_vals, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS) 
# # convert data into 8-bit values 
# centers = np.uint8(centers) 
# segmented_data = centers[labels.flatten()] # Mapping labels to center points( RGB Value)
# # reshape data into the original image dimensions 
# segmented_image = segmented_data.reshape((image.shape)) 
# cv2.imwrite("F://Background removal//output1.png", segmented_image)
# print("done first!")

# ###############################
# # Match the colour of the second image to the first

# # load image from images directory
# image_2 = cv2.imread(file2_path)
# image_2 = match_histograms(image_2, image, channel_axis = -1)
# # Change color to RGB (from BGR)
# image_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2RGB) 
# # Reshaping the image into a 2D array of pixels and 3 color values (RGB) 
# pixel_vals = image_2.reshape((-1,3)) # numpy reshape operation -1 unspecified 
# # Convert to float type only for supporting cv2.kmean
# pixel_vals = np.float32(pixel_vals)
# #criteria
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85) 
# # Choosing number of clusters
# k = groups

# retval, labels, centers = cv2.kmeans(pixel_vals, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS) 
# # convert data into 8-bit values 
# centers = np.uint8(centers) 
# segmented_data = centers[labels.flatten()] # Mapping labels to center points( RGB Value)
# # reshape data into the original image dimensions 
# segmented_image = segmented_data.reshape((image_2.shape)) 
# cv2.imwrite("F://Background removal//output2.png", segmented_image)
# print("done second!")



# # # Updated

# # # remove watermark
# # # colour adjust
# # import sys
# # import cv2
# # import matplotlib.pyplot as plt
# # from skimage import data
# # from skimage import exposure
# # from skimage.exposure import match_histograms
# # import numpy as np

# # input_image1_path = sys.argv[1]
# # input_image2_path = sys.argv[2]
# # threshhold = int(sys.argv[3])

# # # Match the colour of the second image to the first
# # image_1 = cv2.imread(input_image1_path)
# # image_2 = cv2.imread(input_image2_path)
# # image_2 = match_histograms(image_2, image_1, channel_axis = -1)
# # cv2.imwrite("F://Background removal//ADJUSTED_image2.png", image_2)

# # # subtract images in RGB then convert to LAB format
# # subtracted1 = cv2.subtract(image_2, image_1)
# # subtracted2 = cv2.subtract(image_1, image_2)
# # both =  np.maximum(subtracted1, subtracted2)

# # cv2.imwrite("F://Background removal//subtracted_image.png", subtracted1)
# # labified_image = cv2.cvtColor(both, cv2.COLOR_BGR2LAB)

# # # Iterate down comparing two np arrays if one value is different enough than another write out pixels to the third image that is being generated. Other write out a black pixel to that image.
# # for x in range(0, len(labified_image)):
# #     for y in range(0, len(labified_image[x])):
# #         l1, a1, b1 = labified_image[x][y]
# #         # print(l1, a1, b1)
# #         sum = int(l1) + int(a1) - 127 + int(b1) - 127
# #         # print(sum)
# #         if sum < threshhold:
# #             # print("triggered")
# #             # Anywhere sum is below a certain threshhold overwrite original image
# #             image_1[x][y] = (0, 0, 0)

# # # Write out output image
# # cv2.imwrite("F://Background removal//FINALITY.png", image_1)

# # print("done")