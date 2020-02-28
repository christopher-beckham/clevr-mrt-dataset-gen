#!/bin/bash

python generate_questions.py --template_dir CLEVR_TEXT --instances_per_template 3 --output_questions_file ../output/train/CLEVR_questions.json \
  --input_scene_file ../output/train/CLEVR_scenes.json

python generate_questions.py --template_dir CLEVR_TEXT --instances_per_template 3 --output_questions_file ../output/val/CLEVR_questions.json \
  --input_scene_file ../output/val/CLEVR_scenes.json

python generate_questions.py --template_dir CLEVR_TEXT --instances_per_template 3 --output_questions_file ../output/test/CLEVR_questions.json \
  --input_scene_file ../output/test/CLEVR_scenes.json

