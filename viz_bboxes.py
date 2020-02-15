import os
import json
import cv2
import math
import numpy as np

scenes = json.load(open("output/CLEVR_scenes.json", 'r'))
scenes = scenes['scenes']
for scene in scenes:
    img = cv2.imread(os.path.join("output/images/", scene['image_filename']))
    objects = scene['objects']
    for object in objects:
        text = object['text']
        body = text['body']
        char_bboxes = text['char_bboxes']
        for bbox in char_bboxes:
            char = bbox['char']
            o_loc = bbox['center']
            bb = [[int(x), int(y)] for x, y, z in bbox['bbox']]

            # this basically takes the max and min for "normal" left/right top/bottom characters
            bb2 = np.array([[min([bb[0][0], bb[1][0]]), max([bb[0][1], bb[1][1]])],
                            [min([bb[2][0], bb[3][0]]), max([bb[2][1], bb[3][1]])],
                            [max([bb[6][0], bb[7][0]]), max([bb[6][1], bb[7][1]])],
                            [max([bb[4][0], bb[5][0]]), min([bb[4][1], bb[5][1]])]])
            print(char + ": num pixels: " + str(bbox['visible_pixels']))
            # if bbox['visible_pixels'] < 50:
            #     continue

            img = cv2.polylines(img, [bb2], True, (0, 255, 0), 1)

            # use for tweaking bbox locations
            # img = cv2.circle(img, tuple(bb[4]), 2, (0, 0, 255), 1)
            # img = cv2.circle(img, tuple(bb[5]), 2, (0, 0, 255), 1)

            img = cv2.circle(img, tuple(o_loc[0:2]), 2, (0, 0, 255), 1)
            cv2.putText(img, char, tuple(o_loc[0:2]), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)

        # cv2.putText(img,text['body'],tuple(text['pixel_coords'][0:2]),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
    cv2.imwrite('output.png',img)
