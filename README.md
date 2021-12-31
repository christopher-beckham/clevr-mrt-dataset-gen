# Clevr-MRT Dataset

<p align="center">
<img src="https://github.com/christopher-beckham/clevr-mrt-dataset-gen/blob/kiwi_v3/out.gif?raw=true" />
</p>

Different types of mental rotation tests have been used extensively in psychology to understand human visual reasoning and perception. Understanding what an object or visual scene would look like from another viewpoint is a challenging problem that is made even harder if it must be performed from a single image. We explore a controlled setting whereby questions are posed about the properties of a scene if that scene was observed from another viewpoint. To do this we have created a new version of the CLEVR dataset that we call _CLEVR Mental Rotation Tests_ (CLEVR-MRT).

## Exploring dataset

Please see [example.ipynb](example.ipynb).

## Rendering locally (on Mac)

I have rendered some test images locally on Mac as well. At least for me, this is how I did it: create a setup script, I called mine `setup_blender_mac.sh`:

```
#!/bin/bash

# you need blender 2.78
export BLENDER_ROOT="/Applications/Blender_2.78.app/"
export BLENDER="${BLENDER_ROOT}/Contents/MacOS/blender"

# run once:
echo $PWD/image_generation >> ${BLENDER_ROOT}/Contents/Resources/2.78/python/lib/python3.5/site-packages/clevr.pth
```

I simply have this in the root directory of the Clevr repo. Source this setup script file, e.g. `source setup_blender_mac.sh`. Then, in the folder `image_generation` I have a test rendering script, like so:

```
$BLENDER --background --python render_images.py -- \
 --base_scene_blendfile data/base_scene_symmetric.blend \
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
```

## Rendering dataset (in parallel)

TODO

