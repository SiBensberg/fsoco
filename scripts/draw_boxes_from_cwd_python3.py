#!/usr/bin/python

# -*- coding: utf-8 -*-

'''
	Simple script for generating image copies with drawn bounding boxes, using
	darknet format labels and the according images in the cwd.
	
'''

import cv2 as cv
import os
import argparse

colors = {'yellow': (0, 255, 255),
          'blue': (255, 0, 0),
          'red': (0, 0, 255),
          # For daltonics
          'orange': (0, 0, 255),
          'green': (0, 255, 0),
          'pink': (203, 192, 255)}


def get_files(directory, suffix):
    '''
        Returns all files in the 'directory' with the specified suffix
        It's sorted to ensure determinism
    '''
    filenames = os.listdir(directory)
    return sorted([filename for filename in filenames if filename.endswith(suffix)])


def get_class_idx(file_path):
    '''
        Creates a dictionary that maps the classes in the data set to their indices based on the classes doc file
    :param file_path:
    :return: Dictionary
    '''
    idx_to_class_dict = {}
    with open(file_path) as classes_file:
        for idx, line in enumerate(classes_file.readlines()):
            class_name = line.strip()
            idx_to_class_dict[class_name] = idx

    return idx_to_class_dict

def get_class_list(file_path):
    '''
        Generates a list of class names based on classes txt file
    :param file_path:
    :return: List of string class_names
    '''

    class_list = []
    with open(file_path) as classes_file:
        for idx, line in enumerate(classes_file.readlines()):
            class_name = line.strip()
            class_list.append(class_name)

    return class_list

def get_cone_color(class_idx, class_list):
    '''
        Returns the RGB Tuple for the color according to the cone's class
    :param class_idx: Int : Class ID from labels
    :param class_list: List of class names
    :return:
    '''
    cone_color = None
    cone_class = class_list[class_idx]
    for color, rgb in colors.items():
        if color in cone_class:
            cone_color = rgb
    if cone_color is None:
        cone_color = colors['pink']
    return cone_color

def main():
    parser = argparse.ArgumentParser(
        description='Draw Bounding Boxes from label files to copies of according images in the cwd.')
    # parser.usage()
    parser.add_argument('-width', dest='image_width', help='Width of the images', type=int, required=False)
    parser.add_argument('-height', dest='image_height', help='Height of the images', type=int, required=False)
    parser.add_argument('-f', '--format', dest='image_suffix', help='File Suffix of image files', default='jpg',
                        required=False)
    parser.add_argument('-c', '--class_config', dest='class_config_path', help="Text file with row indexed classes",
                        default='classes.txt', required=False)

    argv = parser.parse_args()

    image_suffix = argv.image_suffix

    cwd = os.getcwd()

    image_list = get_files(cwd, image_suffix)
    label_paths = get_files(cwd, "txt")
    # Counter for labels lacking an image
    orphan_labels = 0
    orphan_paths  = []

    # RGB Tuple, 0-255
    # TODO adjust color according to entry index
    class_list = get_class_list(argv.class_config_path)

    for path in label_paths:

        im = None
        
        label_file = open(path)
        label_lines = [line.rstrip("\n") for line in label_file.readlines()]

        rectangle_coords = []

        prefix = path.split('.')[0]
        im = cv.imread(prefix + "." + image_suffix)
        
        # Ignore labels without images and remember orphaned paths
        if im is None:
        
          orphan_labels += 1
          orphan_paths.append(path)
          print ("Couldn't find image in cwd for label: ", path)
          continue
        
        image_height = im.shape[0]
        image_width = im.shape[1]

        for line in label_lines:
            args = line.split(' ')
            clean_args = list(filter(None, args))

            cone_class = int(clean_args[0])
            pixel_bb_x = int(float(clean_args[1]) * image_width)
            pixel_bb_y = int(float(clean_args[2]) * image_height)
            pixel_bb_w = int(float(clean_args[3]) * image_width)
            pixel_bb_h = int(float(clean_args[4]) * image_height)

            upper_right = (int(pixel_bb_x - pixel_bb_w / 2), int(pixel_bb_y - pixel_bb_h / 2))
            lower_left = (int(pixel_bb_x + pixel_bb_w / 2), int(pixel_bb_y + pixel_bb_h / 2))

            rectangle_coords.append(((upper_right, lower_left), cone_class))

        for coords, cone_class in rectangle_coords:
            rectangle_color = get_cone_color(cone_class, class_list)
            cv.rectangle(im, coords[0], coords[1], rectangle_color)

        boxes_image_path = "boxes_" + prefix + "." + image_suffix

        print(
            "Drawing Boxes for image: " + prefix + "." + image_suffix + " into " + "boxes_" + prefix + "." + image_suffix)

        cv.imwrite("boxes_" + prefix + "." + image_suffix, im)
    
    print ("Amount of orphaned labeles: ", orphan_labels)
    print (orphan_paths)

if __name__ == '__main__':
    main()
