#~/.local/bin/blender/blender --background --python render_images.py -- --num_images 1 --width 1920 --height 1080 --use_gpu 1 --max_objects 5 --save_blendfiles 1 --all_chars_visible
#~/.local/bin/blender/blender --background --python render_images.py -- --num_images 1 --width 960 --height 540 --use_gpu 1 --max_objects 3 --all_chars_visible --base_scene_blendfile data/base_scene_tub.blend --enforce_obj_visibility --split text
#~/.local/bin/blender/blender --background --python render_images.py -- --num_images 1 --width 256 --height 256 --use_gpu 1 --max_objects 3 --all_chars_visible --base_scene_blendfile data/base_scene_tub.blend --enforce_obj_visibility --split text


# Generate Clevr-Text
# Generate Train set
~/.local/bin/blender/blender --background --python render_images.py -- --split train-clevr-text \
 --base_scene_blendfile image_generation/data/base_scene_tub.blend \
 --output_image_dir image_generation/output/train-clevr-text/images/ \
 --output_scene_dir image_generation/output/train-clevr-text/scenes/ \
 --output_scene_file image_generation/output/train-clevr-text/CLEVR_scenes.json \
 --enforce_obj_visibility --text --all_chars_visible --num_images 100 --use_gpu 1 --max_objects 3

# Generate Val set
~/.local/bin/blender/blender --background --python render_images.py --  --split val-clevr-text \
 --base_scene_blendfile image_generation/data/base_scene_tub.blend \
 --output_image_dir image_generation/output/val-clevr-text/images/ \
 --output_scene_dir image_generation/output/val-clevr-text/scenes/ \
 --output_scene_file image_generation/output/val-clevr-text/CLEVR_scenes.json \
 --enforce_obj_visibility --text --all_chars_visible --num_images 100 --use_gpu 1 --max_objects 3

## Generate test set
~/.local/bin/blender/blender --background --python render_images.py -- --split test-clevr-text\
 --base_scene_blendfile image_generation/data/base_scene_tub.blend \
 --output_image_dir image_generation/output/test-clevr-text/images/ \
 --output_scene_dir image_generation/output/test-clevr-text/scenes/ \
 --output_scene_file image_generation/output/test-clevr-text/CLEVR_scenes.json \
 --enforce_obj_visibility --text --all_chars_visible --num_images 100 --use_gpu 1 --max_objects 3


# Generate Clevr-Text-PO
# Generate Train set
~/.local/bin/blender/blender --background --python render_images.py -- \
 --base_scene_blendfile image_generation/data/base_scene_tub.blend \
 --output_image_dir image_generation/output/train-clevr-text-po/images/ \
 --output_scene_dir image_generation/output/train-clevr-text-po/scenes/ \
 --output_scene_file image_generation/output/train-clevr-text-po/CLEVR_scenes.json \
 --split train-clevr-text-po \
 --multi_view --text --num_images 100 --use_gpu 1 --max_objects 3 --multi_view --random_text_rotation

# Generate Val set
~/.local/bin/blender/blender --background --python render_images.py -- \
 --base_scene_blendfile image_generation/data/base_scene_tub.blend \
 --output_image_dir image_generation/output/val-clevr-text-po/images/ \
 --output_scene_dir image_generation/output/val-clevr-text-po/scenes/ \
 --output_scene_file image_generation/output/val-clevr-text-po/CLEVR_scenes.json \
 --split val-clevr-text-po \
 --multi_view --text --num_images 100 --use_gpu 1 --max_objects 3 --multi_view --random_text_rotation

## Generate test set
~/.local/bin/blender/blender --background --python render_images.py -- \
 --base_scene_blendfile image_generation/data/base_scene_tub.blend \
 --output_image_dir image_generation/output/test-clevr-text-po/images/ \
 --output_scene_dir image_generation/output/test-clevr-text-po/scenes/ \
 --output_scene_file image_generation/output/test-clevr-text-po/CLEVR_scenes.json \
 --split test-clevr-text-po \
 --multi_view --text --num_images 100 --use_gpu 1 --max_objects 3 --multi_view --random_text_rotation

# Generate Clevr-Kiwi Spatial
# Generate Train set
~/.local/bin/blender/blender --background --python render_images.py -- \
 --base_scene_blendfile image_generation/data/base_scene_symmetric.blend \
 --output_image_dir image_generation/output/train-clevr-kiwi-spatial/images/ \
 --output_scene_dir image_generation/output/train-clevr-kiwi-spatial/scenes/ \
 --output_scene_file image_generation/output/train-clevr-kiwi-spatial/CLEVR_scenes.json \
 --split train-clevr-kiwi-spatial \
 --multi_view --random_views --num_images 1 --use_gpu 1

# Generate Val set
~/.local/bin/blender/blender --background --python render_images.py -- \
 --base_scene_blendfile image_generation/data/base_scene_symmetric.blend \
 --output_image_dir image_generation/output/val-clevr-kiwi-spatial/images/ \
 --output_scene_dir image_generation/output/val-clevr-kiwi-spatial/scenes/ \
 --output_scene_file image_generation/output/val-clevr-kiwi-spatial/CLEVR_scenes.json \
 --split val-clevr-kiwi-spatial \
 --multi_view --random_views --num_images 32 --use_gpu 1

## Generate test set
~/.local/bin/blender/blender --background --python render_images.py -- \
 --base_scene_blendfile image_generation/data/base_scene_symmetric.blend \
 --output_image_dir image_generation/output/test-clevr-kiwi-spatial/images/ \
 --output_scene_dir image_generation/output/test-clevr-kiwi-spatial/scenes/ \
 --output_scene_file image_generation/output/test-clevr-kiwi-spatial/CLEVR_scenes.json \
 --split test-clevr-kiwi-spatial \
 --multi_view --random_views --num_images 32 --use_gpu 1
