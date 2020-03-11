from __future__ import print_function
import argparse, json, os, itertools, random, shutil, string
import time
import re
from collections import defaultdict
import question_engine as qeng


parser = argparse.ArgumentParser()

# Inputs
parser.add_argument('--input_scene_file', default='../output/CLEVR_scenes.json',
    help="JSON file containing ground-truth scene information for all images " +
         "from render_images.py")

# Output
parser.add_argument('--output_ocr_file',
    default='../output/CLEVR_questions.json',
    help="The output file to write containing generated questions")

def main(args):
    try:
        with open(args.input_scene_file, 'r') as f:
                scene_data = json.load(f)
                all_scenes = scene_data['scenes']
    except Exception:
        all_scenes = []
        path = "/".join(args.input_scene_file.split("/")[:-1])
        for subdir in os.listdir(path):
            if not os.path.isdir(subdir):
                continue
            with open(os.path.join(path, subdir, "scenes.json"), 'r') as f:
                scene_data = json.load(f)
                all_scenes.extend(scene_data['scenes'])

    tokens = []
    for i, scene in enumerate(all_scenes):
        scene_fn = scene['cc']['image_filename']
        split = os.path.splitext(scene_fn)[0].split('_')
        if split[-1][0] == 'c':
            image_index = int(split[-2][1:7])  # int(os.path.splitext(scene_fn)[0].split('_')[-1])
        else:
            image_index = int(split[-1][1:7])  # int(os.path.splitext(scene_fn)[0].split('_')[-1])

        view_struct = scene['cc']
        scene_tokens = []
        for object in view_struct['objects']:
            scene_tokens.append({'body': object['text']['body'], 'pixel_coords': object['text']['pixel_coords']})
        print('starting image %s (%d / %d)'
              % (scene_fn, i + 1, len(all_scenes)))
        tokens.append(scene_tokens)

    with open(args.output_ocr_file, 'w') as f:
        print('Writing output to %s' % args.output_ocr_file)
        json.dump({
            'tokens': tokens,
          }, f)




if __name__ == '__main__':
  args = parser.parse_args()
  main(args)

