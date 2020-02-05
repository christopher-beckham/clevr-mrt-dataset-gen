import os
import json
import cv2
import math

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return int(qx), int(qy)


scenes = json.load(open("output/CLEVR_scenes.json", 'r'))
scenes = scenes['scenes']
scene = scenes[0]
img = cv2.imread(os.path.join("output/images/", scene['image_filename']))
objects = scene['objects']
# import pdb; pdb.set_trace()
for object in objects:
    text = object['text']
    body = text['body']
    # img = cv2.rectangle(img, (10, 10), (10, 10), (0, 0, 255), 2)
    char_bboxes = text['char_bboxes']
    # import pdb; pdb.set_trace()
    for bbox in char_bboxes:
        o_loc = bbox[0]
        p1 = (int(bbox[1]), int(bbox[2]))
        p2 = (int(bbox[3]), int(bbox[4]))

        # import pdb; pdb.set_trace()
        w = (p2[0] - p1[0])
        h = (p2[1] - p1[1])
        origin = (p1[0] + w/2, p1[1] + h/2)
        angle = math.pi / 2
        p1 = rotate(origin, p1, angle)
        p2 = rotate(origin, p2, angle)
        print(p1)
        print(p2)
        img = cv2.rectangle(img, p1, p2, (0, 255, 0), 1)
        img = cv2.circle(img, tuple(o_loc[0:2]), 2, (0, 0, 255), 1)
    cv2.putText(img,text['body'],tuple(text['pixel_coords'][0:2]),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
cv2.imwrite('output.png',img)
