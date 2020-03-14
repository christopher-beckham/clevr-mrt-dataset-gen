#!/bin/bash
# Generate CLEVR-text Questions
python question_generation/generate_questions.py \
  --template_dir CLEVR_TEXT \
  --instances_per_template 3 \
  --output_questions_file output/train-clevr-text/CLEVR_questions.json \
  --input_scene_file output/train-clevr-text/CLEVR_scenes.json

python question_generation/generate_questions.py \
  --instances_per_template 3 \
  --template_dir CLEVR_TEXT \
  --output_questions_file output/val-clevr-text/CLEVR_questions.json \
  --input_scene_file output/val-clevr-text/CLEVR_scenes.json

python question_generation/generate_questions.py \
  --template_dir CLEVR_TEXT \
  --instances_per_template 3 \
  --output_questions_file output/test-clevr-text/CLEVR_questions.json \
  --input_scene_file output/test-clevr-text/CLEVR_scenes.json


# Generate Kiwi Spatial Questions
python question_generation/generate_questions.py \
  --template_dir CLEVR_KIWI_SPATIAL \
  --instances_per_template 10 \
  --output_questions_file output/train-clevr-kiwi-spatial/CLEVR_questions.json \
  --input_scene_file output/train-clevr-kiwi-spatial/CLEVR_scenes.json

python question_generation/generate_questions.py \
  --template_dir CLEVR_KIWI_SPATIAL \
  --instances_per_template 10 \
  --output_questions_file output/val-clevr-kiwi-spatial/CLEVR_questions.json \
  --input_scene_file output/val-clevr-kiwi-spatial/CLEVR_scenes.json

python question_generation/generate_questions.py \
  --template_dir CLEVR_KIWI_SPATIAL \
  --instances_per_template 10 \
  --output_questions_file output/test-clevr-kiwi-spatial/CLEVR_questions.json \
  --input_scene_file output/test-clevr-kiwi-spatial/CLEVR_scenes.json

