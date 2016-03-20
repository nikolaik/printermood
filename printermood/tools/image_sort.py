#!/usr/bin/env python
from __future__ import print_function
import argparse
import cv2
import math
import numpy as np
import os
import sys
import uuid


def get_arguments():
    argument_parser = argparse.ArgumentParser(
        description="""Takes and sorts a list of image paths.
        Use arrows to chose the image with best quality. The returned list will
        sort based on best quality first."""
    )
    argument_parser.add_argument(
        'paths',
        metavar='image_path',
        nargs='+',
        help='paths to files to sort'
    )
    return argument_parser.parse_args()


def open_image(path):
    return cv2.imread(path, cv2.IMREAD_COLOR)


def image_dimensions(image):
    height = image.shape[0]
    width = image.shape[1]
    return width, height


def resize_images(image1, image2):
    if image1.shape[0] == image2.shape[0]:
        return image1, image2

    image1_is_bigger = image1.shape[0] > image2.shape[0]

    if image1_is_bigger:
        bigger_image = image1
        smaller_image = image2
    else:
        bigger_image = image2
        smaller_image = image1

    base_height = smaller_image.shape[0]
    target_width = base_height * bigger_image.shape[1] / bigger_image.shape[0]
    bigger_image = cv2.resize(bigger_image, (target_width, base_height))

    if image1_is_bigger:
        return bigger_image, image2
    else:
        return image1, bigger_image


def show_images(path1, path2, window_name=None, separator_size=5, max_height=480):
    if window_name is None:
        window_name = 'Compare'

    image_left = open_image(path1)
    image_right = open_image(path2)

    image_left, image_right = resize_images(image_left, image_right)

    width_left, height_left = image_dimensions(image_left)
    width_right, height_right = image_dimensions(image_right)
    
    total_height = max(height_left, height_right)
    total_width = width_left + separator_size + width_right
    
    separator_image = np.zeros((total_height, separator_size, 3), np.uint8)
    total_image = np.concatenate([image_left, separator_image, image_right], 1)

    resized_height = min(total_height, max_height)
    resized_width = resized_height * total_width / total_height

    cv2.putText(total_image,
                "Use arrows to choose the image with best quality",
                (50, 50),
                cv2.FONT_HERSHEY_PLAIN,
                1.0,
                (0, 0, 0)
    )

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, resized_width, resized_height)
    cv2.imshow(window_name, total_image)
    return window_name


def comparator(path1, path2):
    window_name = show_images(path1, path2)

    try:
        key = cv2.waitKey(0) & 0xff
        if key == 81:  # left_arrow
            return -1
        if key == 83:  # right arrow
            return 1
        if key in [82, 84]:  # top/down arrows
            return 0
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    args = get_arguments()
    do_stop = False
    for path in args.paths:
        if not os.path.exists(path):
            print("File \"{0}\" doesn't exist!".format(path))
            do_stop = True
        else:
            image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if image is None:
                print("File \"{0}\" couldn't be opened!".format(path))
                do_stop=True

    if do_stop:
        sys.exit(1)

    for path in sorted(args.paths, cmp=comparator):
        print(path)
