import os
import json
import cv2

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
        print(p1)
        print(p2)
        img = cv2.rectangle(img, p1, p2, (0, 255, 0), 2)
        img = cv2.circle(img, tuple(o_loc[0:2]), 2, (0, 0, 255), 2)
    cv2.putText(img,text['body'],tuple(text['pixel_coords'][0:2]),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
cv2.imwrite('output.png',img)
