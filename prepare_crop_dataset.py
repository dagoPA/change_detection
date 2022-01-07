import numpy as np
import geeTools
import matplotlib.pyplot as plt
import random
import matplotlib.patches as patches

random.seed(128)
# args
plot = True
im_size = 256
# read image
data_path = '/home/dagopa/data/SAR/'
im = geeTools.readGeoTiffAsRGB(data_path + 'SAR_2019-07-01_2019-08-01.tif')[0]

A = []
B = []
C = []
# split image into slidding windows patches
windows = geeTools.sliding_window(im, 1, (im_size, im_size))
for window in windows:
    im_A = window[2]
    if not np.isnan(im_A).any():
        # prepare arrays for storing results
        im_width = im_A.shape[0]
        im_height = im_A.shape[1]
        im_B = np.copy(im_A)
        im_l = np.zeros((im_width, im_height))

        # random synthetic changes

        # number of pixels that surround the center of the changed clip
        patch_width = random.randint(2, 3)
        patch_height = random.randint(patch_width + 0, patch_width)

        # origin of the patch
        x_o = random.randint(patch_width, im_width - patch_width) - patch_width
        y_o = random.randint(patch_height, im_height - patch_height) - patch_height
        # destination of the patch
        x_d = random.randint(patch_width, im_width - patch_width) - patch_width
        y_d = random.randint(patch_height, im_height - patch_height) - patch_height

        # perform the change
        patch = im_A[x_o - patch_width:x_o + patch_width, y_o - patch_height:y_o + patch_height, 0:2]
        im_B[x_d - patch_width:x_d + patch_width, y_d - patch_height:y_d + patch_height, 0:2] = patch

        im_l[x_d - patch_width:x_d + patch_width, y_d - patch_height:y_d + patch_height] = 1

        # plot
        if plot:
            fig, ax = plt.subplots()
            plt.imshow(im_A[:, :, 0])
            plt.show()

            fig, ax = plt.subplots()
            plt.imshow(im_B[:, :, 0])
            plt.show()

            fig, ax = plt.subplots()
            plt.imshow(im_l)
            plt.show()

        # save the images

        print('completed')


print('eof')
