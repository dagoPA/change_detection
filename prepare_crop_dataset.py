import numpy as np
import geeTools
import matplotlib.pyplot as plt
import random
from PIL import Image

random.seed(128)
# args
plot = True
im_size = 256
# read image
data_path = '/home/dagopa/data/SAR/'

im = geeTools.readGeoTiffAsRGB(data_path + 'SAR_2019-07-01_2019-08-01.tif')[0]

# split image into slidding windows patches
c = 1
windows = geeTools.sliding_window(im, 50, (im_size, im_size))
for window in windows:
    im_A = window[2]
    if not np.isnan(im_A).any():

        # normalize between 0 and 255
        # for bands 0 (HH )and 1 (HV) min is -50 and max is 1
        # for band 2 (angle) min is 0 and max is 90

        im_A = np.uint8(im_A)

        im_A[:, :, 0] = (im_A[:, :, 0] + 50) / 51 * 255
        im_A[:, :, 1] = (im_A[:, :, 1] + 50) / 51 * 255
        im_A[:, :, 2] = (im_A[:, :, 2] / 90) * 255

        # prepare arrays for storing results
        im_width = im_A.shape[0]
        im_height = im_A.shape[1]
        im_B = np.copy(im_A)
        im_l = np.zeros((im_width, im_height))

        # random synthetic changes

        n_changes = random.randint(10, 50)

        for i in range(n_changes):
            # number of pixels that surround the center of the changed clip
            patch_width = random.randint(2, 3)
            patch_height = random.randint(patch_width, patch_width)

            # origin of the patch
            x_o = random.randint(patch_width+1, im_width - patch_width) - patch_width
            y_o = random.randint(patch_height+1, im_height - patch_height) - patch_height
            # destination of the patch
            x_d = random.randint(patch_width+1, im_width - patch_width) - patch_width
            y_d = random.randint(patch_height+1, im_height - patch_height) - patch_height

            # perform the change
            try:
                patch = im_A[x_o - patch_width:x_o + patch_width, y_o - patch_height:y_o + patch_height, 0:2]
                im_B[x_d - patch_width:x_d + patch_width, y_d - patch_height:y_d + patch_height, 0:2] = patch
                im_l[x_d - patch_width:x_d + patch_width, y_d - patch_height:y_d + patch_height] = 255
            except:
                print('error')




            print('patch completed')


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
        A = Image.fromarray(im_A)
        A.save(data_path + 'A/im' + str(c) + '.png')

        B = Image.fromarray(im_B)
        B.save(data_path + 'B/im' + str(c) + '.png')

        # im_l = np.dstack((im_l, im_l, im_l))
        label = Image.fromarray(np.uint8(im_l))
        label.save(data_path + 'labels/im' + str(c) + '.png')

        c = c + 1

print('eof')
