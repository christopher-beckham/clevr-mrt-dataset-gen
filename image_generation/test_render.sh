#!/bin/bash

$BLENDER --background --python render_images.py -- \
 --base_scene_blendfile data/base_scene_symmetric_cone.blend \
 --output_image_dir output/train-clevr-kiwi-spatial/images/ \
 --output_scene_dir output/train-clevr-kiwi-spatial/scenes/ \
 --output_scene_file output/train-clevr-kiwi-spatial/CLEVR_scenes.json \
 --split train-clevr-kiwi-spatial \
 --multi_view --random_views \
 --num_images 10 --use_gpu 0 --render_num_samples 64 \
 --random_view_azimuth_min -180 \
 --random_view_azimuth_max 180 \
 --random_view_elevation_min 30 \
 --random_view_elevation_max 45 \
 --random_view_radius 9
