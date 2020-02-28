#!/bin/bash

python generate_questions.py --template_dir CLEVR_KIWI_SPATIAL --instances_per_template 10 --output_questions_file ../output/train-clevr-kiwi-spatial/CLEVR_questions.json \
  --input_scene_file ../output/train-clevr-kiwi-spatial/CLEVR_scenes.json

#python generate_questions.py --template_dir CLEVR_TEXT --instances_per_template 10 --output_questions_file ../output/val-clevr-kiwi-spatial/CLEVR_questions.json \
#  --input_scene_file ../output/val-clevr-kiwi-spatial/CLEVR_scenes.json
#
#python generate_questions.py --template_dir CLEVR_TEXT --instances_per_template 10 --output_questions_file ../output/test-clevr-kiwi-spatial/CLEVR_questions.json \
#  --input_scene_file ../output/test-clevr-kiwi-spatial/CLEVR_scenes.json
#
