# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from __future__ import print_function
import math, sys, argparse, json, os, tempfile, string
from datetime import datetime as dt
from collections import Counter
from random import uniform, randint, choice, random
import builtins as __builtin__
import numpy as np

"""
Renders random scenes using Blender, each with with a random number of objects;
each object has a random size, position, color, and shape. Objects will be
nonintersecting but may partially occlude each other. Output images will be
written to disk as PNGs, and we will also write a JSON file for each image with
ground-truth scene information.

This file expects to be run from Blender like this:

blender --background --python render_images.py -- [arguments to this script]
"""

PI = math.pi

INSIDE_BLENDER = True
try:
    import bpy, bpy_extras
    from mathutils import Vector
except ImportError as e:
    INSIDE_BLENDER = False
if INSIDE_BLENDER:
    try:
        import utils
    except ImportError as e:
        print("\nERROR")
        print("Running render_images.py from Blender and cannot import utils.py.")
        print("You may need to add a .pth file to the site-packages of Blender's")
        print("bundled python with a command like this:\n")
        print("echo $PWD >> $BLENDER/$VERSION/python/lib/python3.5/site-packages/clevr.pth")
        print("\nWhere $BLENDER is the directory where Blender is installed, and")
        print("$VERSION is your Blender version (such as 2.78).")
        sys.exit(1)

parser = argparse.ArgumentParser()

# Input options
parser.add_argument(
    "--base_scene_blendfile",
    default="data/base_scene.blend",
    help="Base blender file on which all scenes are based; includes " + "ground plane, lights, and camera.",
)
parser.add_argument(
    "--properties_json",
    default="data/properties.json",
    help="JSON file defining objects, materials, sizes, and colors. "
    + 'The "colors" field maps from CLEVR color names to RGB values; '
    + 'The "sizes" field maps from CLEVR size names to scalars used to '
    + 'rescale object models; the "materials" and "shapes" fields map '
    + "from CLEVR material and shape names to .blend files in the "
    + "--object_material_dir and --shape_dir directories respectively.",
)
parser.add_argument(
    "--shape_dir", default="data/shapes", help="Directory where .blend files for object models are stored"
)
parser.add_argument(
    "--material_dir", default="data/materials", help="Directory where .blend files for materials are stored"
)
parser.add_argument(
    "--shape_color_combos_json",
    default=None,
    help="Optional path to a JSON file mapping shape names to a list of "
    + "allowed color names for that shape. This allows rendering images "
    + "for CLEVR-CoGenT.",
)

# Settings for objects
parser.add_argument("--min_objects", default=3, type=int, help="The minimum number of objects to place in each scene")
parser.add_argument("--max_objects", default=10, type=int, help="The maximum number of objects to place in each scene")
parser.add_argument("--min_dist", default=0.25, type=float, help="The minimum allowed distance between object centers")
parser.add_argument(
    "--margin",
    default=0.4,
    type=float,
    help="Along all cardinal directions (left, right, front, back), all "
    + "objects will be at least this distance apart. This makes resolving "
    + "spatial relationships slightly less ambiguous.",
)
parser.add_argument(
    "--min_pixels_per_object",
    default=200,
    type=int,
    help="All objects will have at least this many visible pixels in the "
    + "final rendered images; this ensures that no objects are fully "
    + "occluded by other objects.",
)
parser.add_argument(
    "--min_char_pixels",
    default=1,
    type=int,
    help="All objects will have at least this many visible pixels in the "
    + "final rendered images; this ensures that no objects are fully "
    + "occluded by other objects.",
)
parser.add_argument(
    "--max_retries",
    default=50,
    type=int,
    help="The number of times to try placing an object before giving up and " + "re-placing all objects in the scene.",
)

# Settings for text
parser.add_argument(
    "--random_text_rotation", action="store_true", help="Determines whether the text will be rotated around the object"
)
parser.add_argument("--text", action="store_true", help="Determines whether there will be text on the objects.")
parser.add_argument(
    "--all_chars_visible",
    action="store_true",
    help="Determines whether we require that all text characters are visible from one view",
)
parser.add_argument("--multi_view", action="store_true", help="should we write out multiple views")
parser.add_argument("--max_texts_per_obj", default=1, type=int, help="max number of pieces of text to put on each obj")
parser.add_argument("--shadow_less", action="store_true", help="don't render shadows")
parser.add_argument(
    "--random_views", action="store_true", help="should we sample different view positions around the scene"
)
parser.add_argument(
    "--random_view_azimuth_min",
    default=0,
    type=float,
    help="rotation/azimuth lower bound in degrees, can be negative, default: 0",
)
parser.add_argument(
    "--random_view_azimuth_max", default=360, type=float, help="rotation/azimuth upper bound in deg, default: 360",
)
parser.add_argument(
    "--random_view_radius", default=10.0, type=float, help="radius for cameras for random rotation",
)

parser.add_argument(
    "--random_view_elevation_min", default=25, type=float, help="elevation lower bound in deg, default: 25",
)
parser.add_argument(
    "--random_view_elevation_max", default=60, type=float, help="rotation upper bound, default: 60",
)

parser.add_argument(
    "--enforce_obj_visibility", action="store_true", help="should all objects be visible from canonical view?"
)

# Output settings
parser.add_argument(
    "--start_idx",
    default=0,
    type=int,
    help="The index at which to start for numbering rendered images. Setting "
    + "this to non-zero values allows you to distribute rendering across "
    + "multiple machines and recombine the results later.",
)
parser.add_argument("--num_images", default=5, type=int, help="The number of images to render")
parser.add_argument(
    "--filename_prefix", default="CLEVR", help="This prefix will be prepended to the rendered images and JSON scenes"
)
parser.add_argument(
    "--split",
    default="new",
    help="Name of the split for which we are rendering. This will be added to "
    + "the names of rendered images, and will also be stored in the JSON "
    + "scene structure for each image.",
)
parser.add_argument(
    "--output_image_dir",
    default="../output/images/",
    help="The directory where output images will be stored. It will be " + "created if it does not exist.",
)
parser.add_argument(
    "--output_scene_dir",
    default="../output/scenes/",
    help="The directory where output JSON scene structures will be stored. "
    + "It will be created if it does not exist.",
)
parser.add_argument(
    "--output_scene_file",
    default="../output/CLEVR_scenes.json",
    help="Path to write a single JSON file containing all scene information",
)
parser.add_argument(
    "--output_blend_dir",
    default="output/blendfiles",
    help="The directory where blender scene files will be stored, if the "
    + "user requested that these files be saved using the "
    + "--save_blendfiles flag; in this case it will be created if it does "
    + "not already exist.",
)
parser.add_argument(
    "--save_blendfiles",
    type=int,
    default=0,
    help="Setting --save_blendfiles 1 will cause the blender scene file for "
    + "each generated image to be stored in the directory specified by "
    + "the --output_blend_dir flag. These files are not saved by default "
    + "because they take up ~5-10MB each.",
)
parser.add_argument(
    "--version", default="1.data", help='String to store in the "version" field of the generated JSON file'
)
parser.add_argument(
    "--license",
    default="Creative Commons Attribution (CC-BY 4.data)",
    help='String to store in the "license" field of the generated JSON file',
)
parser.add_argument(
    "--date",
    default=dt.today().strftime("%m/%d/%Y"),
    help='String to store in the "date" field of the generated JSON file; ' + "defaults to today's date",
)

# Rendering options
parser.add_argument(
    "--use_gpu",
    default=0,
    type=int,
    help="Setting --use_gpu 1 enables GPU-accelerated rendering using CUDA. "
    + "You must have an NVIDIA GPU with the CUDA toolkit installed for "
    + "to work.",
)
parser.add_argument("--width", default=320, type=int, help="The width (in pixels) for the rendered images")
parser.add_argument("--height", default=240, type=int, help="The height (in pixels) for the rendered images")
parser.add_argument(
    "--key_light_jitter",
    default=1.0,
    type=float,
    help="The magnitude of random jitter to add to the key light position.",
)
parser.add_argument(
    "--fill_light_jitter",
    default=1.0,
    type=float,
    help="The magnitude of random jitter to add to the fill light position.",
)
parser.add_argument(
    "--back_light_jitter",
    default=1.0,
    type=float,
    help="The magnitude of random jitter to add to the back light position.",
)
parser.add_argument(
    "--camera_jitter", default=0.5, type=float, help="The magnitude of random jitter to add to the camera position"
)
parser.add_argument(
    "--render_num_samples",
    default=512,
    type=int,
    help="The number of samples to use when rendering. Larger values will "
    + "result in nicer images but will cause rendering to take longer.",
)
parser.add_argument(
    "--render_min_bounces", default=8, type=int, help="The minimum number of bounces to use for rendering."
)
parser.add_argument(
    "--render_max_bounces", default=8, type=int, help="The maximum number of bounces to use for rendering."
)
parser.add_argument(
    "--render_tile_size",
    default=256,
    type=int,
    help="The tile size to use for rendering. This should not affect the "
    + "quality of the rendered image but may affect the speed; CPU-based "
    + "rendering may achieve better performance using smaller tile sizes "
    + "while larger tile sizes may be optimal for GPU-based rendering.",
)


def main(args):

    if not os.path.isdir(args.output_image_dir):
        os.makedirs(args.output_image_dir)
    if not os.path.isdir(args.output_scene_dir):
        os.makedirs(args.output_scene_dir)
    if args.save_blendfiles == 1 and not os.path.isdir(args.output_blend_dir):
        os.makedirs(args.output_blend_dir)

    all_scene_paths = []
    for i in range(args.num_images):
        prefix = "%s_%s_" % (args.filename_prefix, args.split)

        img_path = prefix + "s" + str((i + args.start_idx)).zfill(6) + ".png"
        scene_path = img_path.replace(".png", ".json")
        blend_path = img_path.replace(".png", ".blend")

        img_path = os.path.join(args.output_image_dir, img_path)
        scene_path = os.path.join(args.output_scene_dir, scene_path)
        blend_path = os.path.join(args.output_blend_dir, blend_path)

        all_scene_paths.append(scene_path)
        num_objects = randint(args.min_objects, args.max_objects)
        render_scene(
            args,
            num_objects=num_objects,
            output_index=(i + args.start_idx),
            output_split=args.split,
            output_image=img_path,
            output_scene=scene_path,
            output_blendfile=blend_path,
        )

    # After rendering all images, combine the JSON files for each scene into a
    # single JSON file.
    all_scenes = []
    for scene_path in all_scene_paths:
        with open(scene_path, "r") as f:
            all_scenes.append(json.load(f))
    output = {
        "info": {"date": args.date, "version": args.version, "split": args.split, "license": args.license,},
        "scenes": all_scenes,
    }
    with open(args.output_scene_file, "w") as f:
        json.dump(output, f)


def render_scene(
    args,
    num_objects=5,
    output_index=0,
    output_split="none",
    output_image="render.png",
    output_scene="render_json",
    output_blendfile=None,
):

    # Load the main blendfile
    bpy.ops.wm.open_mainfile(filepath=args.base_scene_blendfile)

    # Load materials
    utils.load_materials(args.material_dir)

    # Set render arguments so we can get pixel coordinates later.
    # We use functionality specific to the CYCLES renderer so BLENDER_RENDER
    # cannot be used.
    render_args = bpy.context.scene.render
    render_args.engine = "CYCLES"
    render_args.filepath = output_image
    render_args.resolution_x = args.width
    render_args.resolution_y = args.height
    render_args.resolution_percentage = 100
    render_args.tile_x = args.render_tile_size
    render_args.tile_y = args.render_tile_size

    bpy.context.scene.render.engine = "CYCLES"

    if args.use_gpu == 1:
        # Blender changed the API for enabling CUDA at some point
        if bpy.app.version < (2, 78, 0):
            bpy.context.user_preferences.system.compute_device_type = "CUDA"
            bpy.context.user_preferences.system.compute_device = "CUDA_0"
        else:
            cycles_prefs = bpy.context.user_preferences.addons["cycles"].preferences
            cycles_prefs.compute_device_type = "CUDA"

    # Some CYCLES-specific stuff
    bpy.data.worlds["World"].cycles.sample_as_light = True
    bpy.context.scene.cycles.blur_glossy = 2.0
    bpy.context.scene.cycles.samples = args.render_num_samples
    bpy.context.scene.cycles.transparent_min_bounces = args.render_min_bounces
    bpy.context.scene.cycles.transparent_max_bounces = args.render_max_bounces
    if args.use_gpu == 1:
        bpy.context.scene.cycles.device = "GPU"

    # This will give ground-truth information about the scene and its objects
    view_struct = {}
    if args.multi_view:
        cams = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
        poses = [cam.location for cam in cams]

        if args.random_views:

            base_angle = math.atan2(cams[0].location[1], cams[0].location[0])

            num_samples = 20
            # generate the points on a circle of radius r around the scene
            azimuths = [
                uniform(base_angle + args.random_view_azimuth_min, base_angle + args.random_view_azimuth_max)
                for _ in range(num_samples)
            ]
            x = [args.random_view_radius * math.cos(a) for a in azimuths]
            y = [args.random_view_radius * math.sin(a) for a in azimuths]
            elevations = [
                uniform(args.random_view_elevation_min, args.random_view_elevation_max) for _ in range(num_samples)
            ]
            z = [math.tan(e) * args.random_view_radius for e in elevations]

            for z_i in z:
                if z_i < 2:
                    print(
                        "\n\n=== WARNING: ELEVATION VERY LOW ({}). "
                        "PROLLY HARD TO FIND WORKING CONFIGURATION WHERE NOTHING IS OBSCURED.\n"
                        "Increase args.random_view_elevation_min\n\n".format(z_i)
                    )

            scn = bpy.context.scene
            origin_empty = cams[0].constraints[0].target
            cams = [cams[0]]
            for i in range(num_samples):

                # create the first camera
                cam = bpy.data.cameras.new("cam" + str(i))

                # create the first camera object
                cam_obj = bpy.data.objects.new("cam" + str(i), cam)
                cam_obj.location = (x[i], y[i], z[i])

                print("cam_obj loc", cam_obj.location)

                m = cam_obj.constraints.new("TRACK_TO")
                m.target = origin_empty
                m.track_axis = "TRACK_NEGATIVE_Z"
                m.up_axis = "UP_Y"
                scn.objects.link(cam_obj)
                cams.append(cam_obj)
    else:
        cams = [obj for obj in bpy.data.objects if obj.name == "cc"]
    if args.multi_view:
        bpy.context.scene.update()

        for idx, cam in enumerate(cams):

            path_dir = bpy.context.scene.render.filepath
            path = ".".join(path_dir.split(".")[:-1]) + "_" + cam.name + ".png"
            # 6 total parameters defining the xyz location and xyz rotation (in radians) of the camera

            cam_params = list(cam.location[:]) + list(cam.matrix_world.to_euler("XYZ")[:])
            view_struct[cam.name] = {
                "split": output_split,
                "image_index": output_index + idx,
                "image_filename": os.path.basename(path.split("/")[-1]),
                "objects": [],
                "directions": {},
                "cam_params": cam_params,
            }
    else:
        cam_params = list(cams[0].location[:]) + list(cams[0].rotation_euler[:])
        view_struct["cc"] = {
            "split": output_split,
            "image_index": output_index,
            "image_filename": os.path.basename(output_image),
            "objects": [],
            "directions": {},
            "cam_params": cam_params,
        }

    # Put a plane on the ground so we can compute cardinal directions
    bpy.ops.mesh.primitive_plane_add(radius=5)
    plane = bpy.context.object

    def rand(L):
        return 2.0 * L * (random() - 0.5)

    # Add random jitter to camera position
    if args.camera_jitter > 0:
        for cam in cams:
            for i in range(3):
                cam.location[i] += rand(args.camera_jitter)
            # cam.location[2] = 2

    # Figure out the left, up, and behind directions along the plane and record
    # them in the scene structure
    camera = bpy.data.objects["cc"]
    # Quaternion((0.781359076499939, 0.46651220321655273, 0.2125076949596405, 0.3559281527996063))
    plane_normal = plane.data.vertices[0].normal
    cam_behind = camera.matrix_world.to_quaternion() * Vector((0, 0, -1))
    cam_left = camera.matrix_world.to_quaternion() * Vector((-1, 0, 0))
    cam_up = camera.matrix_world.to_quaternion() * Vector((0, 1, 0))
    plane_behind = (cam_behind - cam_behind.project(plane_normal)).normalized()
    plane_left = (cam_left - cam_left.project(plane_normal)).normalized()
    plane_up = cam_up.project(plane_normal).normalized()

    # Delete the plane; we only used it for normals anyway. The base scene file
    # contains the actual ground plane.
    utils.delete_object(plane)

    # Save all six axis-aligned directions in the scene struct
    view_struct["cc"]["directions"]["behind"] = tuple(plane_behind)
    view_struct["cc"]["directions"]["front"] = tuple(-plane_behind)
    view_struct["cc"]["directions"]["left"] = tuple(plane_left)
    view_struct["cc"]["directions"]["right"] = tuple(-plane_left)
    view_struct["cc"]["directions"]["above"] = tuple(plane_up)
    view_struct["cc"]["directions"]["below"] = tuple(-plane_up)

    # Add random jitter to lamp positions
    if args.key_light_jitter > 0:
        for i in range(3):
            bpy.data.objects["Lamp_Key"].location[i] += rand(args.key_light_jitter)
    if args.back_light_jitter > 0:
        for i in range(3):
            bpy.data.objects["Lamp_Back"].location[i] += rand(args.back_light_jitter)
    if args.fill_light_jitter > 0:
        for i in range(3):
            bpy.data.objects["Lamp_Fill"].location[i] += rand(args.fill_light_jitter)

    # Now make some random objects
    texts, blender_texts, objects, blender_objects = add_random_objects(view_struct, num_objects, args, cams)

    if args.shadow_less:
        for obj in blender_objects:
            bpy.context.scene.objects.active = obj
            bpy.context.object.cycles_visibility.shadow = False

    # Render the scene and dump the scene data structure
    for cam in cams:
        view_struct[cam.name]["objects"] = objects[cam.name]
        view_struct[cam.name]["texts"] = texts
        view_struct[cam.name]["relationships"] = compute_all_relationships(view_struct)
    while True:
        try:
            path_dir = bpy.context.scene.render.filepath  # save for restore
            if args.multi_view:
                for cam in cams:
                    bpy.context.scene.camera = cam
                    bpy.context.scene.render.filepath = ".".join(path_dir.split(".")[:-1]) + "_" + cam.name + ".png"
                    bpy.ops.render.render(write_still=True)
                    bpy.context.scene.render.filepath = path_dir
            else:
                bpy.ops.render.render(write_still=True)
            break

        except Exception as e:
            print(e)

    with open(output_scene, "w") as f:
        json.dump(view_struct, f, indent=2)

    if args.save_blendfiles:
        bpy.ops.wm.save_as_mainfile(filepath=output_blendfile)


def add_random_objects(view_struct, num_objects, args, cams):
    """
  Add random objects to the current blender scene
  """

    # Load the property file
    with open(args.properties_json, "r") as f:
        properties = json.load(f)
        color_name_to_rgba = {}
        for name, rgb in properties["colors"].items():
            rgba = [float(c) / 255.0 for c in rgb] + [1.0]
            color_name_to_rgba[name] = rgba
        material_mapping = [(v, k) for k, v in properties["materials"].items()]
        object_mapping = [(v, k) for k, v in properties["shapes"].items()]
        size_mapping = list(properties["sizes"].items())

    shape_color_combos = None
    if args.shape_color_combos_json is not None:
        with open(args.shape_color_combos_json, "r") as f:
            shape_color_combos = list(json.load(f).items())

    positions = []
    objects = {cam.name: [] for cam in cams}
    blender_objects = []
    texts = []
    blender_texts = []
    all_chars = []
    for i in range(num_objects):
        # Choose a random size
        size_name, r = choice(size_mapping)

        # Try to place the object, ensuring that we don't intersect any existing
        # objects and that we are more than the desired margin away from all existing
        # objects along all cardinal directions.
        num_tries = 0
        while True:
            # If we try and fail to place an object too many times, then delete all
            # the objects in the scene and start over.
            num_tries += 1
            if num_tries > args.max_retries:
                for obj in blender_objects:
                    utils.delete_object(obj)
                for text in blender_texts:
                    utils.delete_object(text)
                return add_random_objects(view_struct, num_objects, args, cams)
            x = uniform(-3, 3)
            y = uniform(-3, 3)
            # Check to make sure the new object is further than min_dist from all
            # other objects, and further than margin along the four cardinal directions
            dists_good = True
            margins_good = True
            for (xx, yy, rr) in positions:
                dx, dy = x - xx, y - yy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist - r - rr < args.min_dist:
                    dists_good = False
                    break
                for direction_name in ["left", "right", "front", "behind"]:
                    direction_vec = view_struct["cc"]["directions"][direction_name]
                    assert direction_vec[2] == 0
                    margin = dx * direction_vec[0] + dy * direction_vec[1]
                    if 0 < margin < args.margin:
                        __builtin__.print(margin, args.margin, direction_name)
                        __builtin__.print("BROKEN MARGIN!")
                        margins_good = False
                        break
                if not margins_good:
                    break

            if dists_good and margins_good:
                break

        # Choose random color and shape
        if shape_color_combos is None:
            obj_name, obj_name_out = choice(object_mapping)
            color_name, rgba = choice(list(color_name_to_rgba.items()))
        else:
            obj_name_out, color_choices = choice(shape_color_combos)
            color_name = choice(color_choices)
            obj_name = [k for k, v in object_mapping if v == obj_name_out][0]
            rgba = color_name_to_rgba[color_name]

        # For cube, adjust the size a bit
        if obj_name == "Cube":
            r /= math.sqrt(2)

        # Choose random orientation for the object.
        theta = 360.0 * random()

        # Actually add the object to the scene
        utils.add_object(args.shape_dir, obj_name, r, (x, y), theta=theta)
        obj = bpy.context.object
        blender_objects.append(obj)
        positions.append((x, y, r))
        __builtin__.print("added random object " + str(i))

        # Attach a random material
        mat_name, mat_name_out = choice(material_mapping)
        utils.add_material(mat_name, Color=rgba)

        # Record data about the object in the scene data structure
        for cam in cams:
            pixel_coords = utils.get_camera_coords(cam, obj.location)
            objects[cam.name].append(
                {
                    "shape": obj_name_out,
                    "size": size_name,
                    "material": mat_name_out,
                    "3d_coords": tuple(obj.location),
                    "rotation": theta,
                    "pixel_coords": pixel_coords,
                    "color": color_name,
                }
            )

        # Generate Text

        # Add text to Blender
        if args.text:
            all_word_bboxes = []
            all_char_bboxes = []
            for i in range(np.random.randint(1, args.max_texts_per_obj + 1)):
                num_chars = 1  # random.choice(range(1, 7))
                chars = choice(
                    string.ascii_lowercase
                )  # "".join([random.choice(string.printable[:36]) for _ in range(num_chars)])

                try:
                    out_word_bboxes, out_char_bboxes, out_chars = utils.add_text(chars, args.random_text_rotation, cams)
                    all_chars.extend(out_chars)
                    all_word_bboxes.extend(out_word_bboxes)
                    all_char_bboxes.extend(out_char_bboxes)
                    # Select material and color for text
                    text = bpy.context.scene.objects.active
                    temp_dict = color_name_to_rgba.copy()
                    del temp_dict[color_name]
                    mat_name, mat_name_out = choice(material_mapping)
                    color_name, rgba = choice(list(temp_dict.items()))
                    utils.add_material(mat_name, Color=rgba)

                    for char in out_chars:
                        bpy.context.scene.objects.active = char
                        utils.add_material(mat_name, Color=rgba)

                except Exception as e:
                    return purge(blender_objects, blender_texts, view_struct, num_objects, args, cams)

            blender_texts.append(text)
            __builtin__.print("added text to object " + str(i))

            # Check that all objects are at least partially visible in the rendered image
            for cam in cams:
                bpy.context.scene.camera = cam
                all_objects_visible, visible_chars = check_visibility(
                    blender_objects + all_chars, args.min_pixels_per_object, cams
                )
                for textid, visible_pixels in visible_chars.items():
                    for char_bbox in all_char_bboxes[cam.name]:
                        if char_bbox["id"] == textid:
                            char_bbox["visible_pixels"] = visible_pixels
            all_chars_visible = [c["visible_pixels"] > args.min_char_pixels for c in all_char_bboxes["cc"]]
            if args.all_chars_visible and not all(all_chars_visible):
                __builtin__.print("not all characters were visible, purging and retrying...")
                return purge(blender_objects, blender_texts, view_struct, num_objects, args, cams)

            for cam in cams:
                x, y, _ = utils.get_camera_coords(cam, text.location)
                objects[cam.name][-1]["text"] = {
                    "font": text.data.font.name,
                    "body": text.data.body,
                    "3d_coords": tuple(text.location),
                    "pixel_coords": (
                        x / bpy.context.scene.render.resolution_x,
                        y / bpy.context.scene.render.resolution_y,
                    ),
                    "color": color_name,
                    "char_bboxes": all_char_bboxes,
                    "word_bboxes": all_word_bboxes,
                }
        else:
            all_objects_visible, visible_chars = check_visibility(
                blender_objects + all_chars, args.min_pixels_per_object, cams
            )

    if args.enforce_obj_visibility and not all_objects_visible:
        __builtin__.print("not all objects were visible, purging and retrying...")
        return purge(blender_objects, blender_texts, view_struct, num_objects, args, cams)

    return texts, blender_texts, objects, blender_objects


def purge(blender_objects, blender_texts, view_struct, num_objects, args, cams):
    # If any of the objects are fully occluded then start over; delete all
    # objects from the scene and place them all again.
    __builtin__.print("Some objects are occluded; replacing objects")
    for obj in blender_objects:
        utils.delete_object(obj)
    for text in blender_texts:
        utils.delete_object(text)
    for obj in bpy.context.scene.objects:
        if "Text" in obj.name:
            utils.delete_object(obj)
    return add_random_objects(view_struct, num_objects, args, cams)


def compute_all_relationships(view_struct, eps=0.2):
    """
  Computes relationships between all pairs of objects in the scene.
  
  Returns a dictionary mapping string relationship names to lists of lists of
  integers, where output[rel][i] gives a list of object indices that have the
  relationship rel with object i. For example if j is in output['left'][i] then
  object j is left of object i.
  """
    all_relationships = {}
    for name, direction_vec in view_struct["cc"]["directions"].items():
        if name == "above" or name == "below":
            continue
        all_relationships[name] = []
        for i, obj1 in enumerate(view_struct["cc"]["objects"]):
            coords1 = obj1["3d_coords"]
            related = set()
            for j, obj2 in enumerate(view_struct["cc"]["objects"]):
                if obj1 == obj2:
                    continue
                coords2 = obj2["3d_coords"]
                diff = [coords2[k] - coords1[k] for k in [0, 1, 2]]
                dot = sum(diff[k] * direction_vec[k] for k in [0, 1, 2])
                if dot > eps:
                    related.add(j)
            all_relationships[name].append(sorted(list(related)))
    return all_relationships


def check_visibility(blender_objects, min_pixels_per_object, cams):
    """
  Check whether all objects in the scene have some minimum number of visible
  pixels; to accomplish this we assign random (but distinct) colors to all
  objects, and render using no lighting or shading or antialiasing; this
  ensures that each object is just a solid uniform color. We can then count
  the number of pixels of each color in the output image to check the visibility
  of each object.

  Returns True if all objects are visible and False otherwise.
  """

    # Split up input objects into characters and objects
    num_visible_obs = 0
    chars = []
    objs = []
    for obj in blender_objects:
        __builtin__.print(obj.data.name)
        if "Mesh" in obj.data.name or "CUText" in obj.data.name:
            chars.append(obj)
        else:
            objs.append(obj)

    # render an image with different colors for each object and count the pixels (ignoring alpha)
    f, path = tempfile.mkstemp(suffix=".exr")
    object_colors, text_colors = render_shadeless(blender_objects, path=path)
    img = bpy.data.images.load(path)
    __builtin__.print(img)
    p = list(img.pixels)
    color_count = Counter((p[i], p[i + 1], p[i + 2]) for i in range(0, len(p), 4))
    os.remove(path)

    # loop through the colors and match them to objects (and characters)
    visible_chars = {}
    i = 0
    for color, count in color_count.most_common():
        if i != 0:
            color = (round(color[0], 2), round(color[1], 2), round(color[2], 2))
        i += 1
        was_text, text_name = color_in_colors(color, text_colors)
        was_obj = color_in_objcolors(color, object_colors)
        if was_text:
            visible_chars[text_name] = count
        if was_obj and count > min_pixels_per_object:
            num_visible_obs += 1
    if num_visible_obs == len(objs):
        return True, visible_chars
    return False, visible_chars


def color_in_colors(color, text_colors):
    tname = None
    for tname, tc in text_colors.items():
        if color == tc:
            return True, tname
    return False, tname


def color_in_objcolors(color, obj_colors):
    for c in obj_colors:
        if color == c:
            return True
    return False


def render_shadeless(blender_objects, path="flat.png"):
    """
  Render a version of the scene with shading disabled and unique materials
  assigned to all objects, and return a set of all colors that should be in the
  rendered image. The image itself is written to path. This is used to ensure
  that all objects will be visible in the final rendered scene.
  """
    render_args = bpy.context.scene.render

    # Cache the render args we are about to clobber
    old_filepath = render_args.filepath
    old_engine = render_args.engine
    old_use_antialiasing = render_args.use_antialiasing

    # Override some render settings to have flat shading
    render_args.filepath = path
    render_args.engine = "BLENDER_RENDER"
    render_args.use_antialiasing = False

    # Move the lights and ground to layer 2 so they don't render
    utils.set_layer(bpy.data.objects["Lamp_Key"], 2)
    utils.set_layer(bpy.data.objects["Lamp_Fill"], 2)
    utils.set_layer(bpy.data.objects["Lamp_Back"], 2)
    utils.set_layer(bpy.data.objects["Ground"], 2)

    # Add random shadeless materials to all objects
    object_colors = set()
    text_colors = {}
    old_materials = []

    for i, obj in enumerate(blender_objects):
        old_materials.append(obj.data.materials[0])
        bpy.ops.material.new()
        mat = bpy.data.materials["Material"]
        mat.name = "Material_%d" % i
        r, g, b = i * 0.01, i * 0.01, i * 0.01

        if "Mesh" in obj.data.name or "CUText" in obj.data.name:
            text_colors[obj.data.name] = (r, g, b)
        else:
            object_colors.add((r, g, b))
        mat.diffuse_color = [r, g, b]
        mat.use_shadeless = True
        obj.data.materials[0] = mat

    # Need to do this to not transform the colors too much during rendering
    bpy.context.scene.render.image_settings.view_settings.view_transform = "Raw"
    bpy.context.scene.render.image_settings.file_format = "OPEN_EXR"
    bpy.context.scene.render.image_settings.color_mode = "RGB"
    bpy.context.scene.render.engine = "CYCLES"  # just making sure

    # Render the scene
    bpy.ops.render.render(write_still=True)

    # Change these settings back so we render out the PNG images
    bpy.context.scene.render.image_settings.view_settings.view_transform = "Default"
    bpy.context.scene.render.image_settings.file_format = "JPEG"
    bpy.context.scene.render.image_settings.color_mode = "RGB"

    # Undo the above; first restore the materials to objects
    for mat, obj in zip(old_materials, blender_objects):
        obj.data.materials[0] = mat

    # Move the lights and ground back to layer data
    utils.set_layer(bpy.data.objects["Lamp_Key"], 0)
    utils.set_layer(bpy.data.objects["Lamp_Fill"], 0)
    utils.set_layer(bpy.data.objects["Lamp_Back"], 0)
    utils.set_layer(bpy.data.objects["Ground"], 0)

    # Set the render settings back to what they were
    render_args.filepath = old_filepath
    render_args.engine = old_engine
    render_args.use_antialiasing = old_use_antialiasing

    return object_colors, text_colors


# I removed the "if _nname__ == main here because it's ALWAYS main.
# Nobody calls functions of this file from somewhere else.

if INSIDE_BLENDER:
    # Run normally
    argv = utils.extract_args()
    args = parser.parse_args(argv)

    ### azimuth stuff
    if args.random_view_azimuth_min > args.random_view_azimuth_max:
        # swap it
        args.random_view_azimuth_max, args.random_view_azimuth_min = (
            args.random_view_azimuth_min,
            args.random_view_azimuth_max,
        )
    if args.random_view_azimuth_max > 360:
        print("FYI: 360 is a full rotation and you specified {} as max".format(args.random_view_azimuth_max))
    args.random_view_azimuth_min = math.radians(args.random_view_azimuth_min)
    args.random_view_azimuth_max = math.radians(args.random_view_azimuth_max)

    assert 0.001 <= args.random_view_radius <= 100

    ### elevation stuff
    if args.random_view_elevation_min > args.random_view_elevation_max:
        args.random_view_elevation_min, args.random_view_elevation_max = (
            args.random_view_elevation_max,
            args.random_view_elevation_min,
        )

    assert 0 < args.random_view_elevation_min <= args.random_view_elevation_max < 90
    if args.random_view_elevation_min < 10:
        print("\n\nWARNING: low elevation angle. Might take long to find non-obstructed perspective\n\n")
    args.random_view_elevation_min = math.radians(args.random_view_elevation_min)
    args.random_view_elevation_max = math.radians(args.random_view_elevation_max)

    ### main prog
    arg_names = sorted(vars(args))
    for arg in arg_names:
        print("{:>25} {}".format(arg, getattr(args, arg)))

    main(args)
elif "--help" in sys.argv or "-h" in sys.argv:
    parser.print_help()
else:
    print("This script is intended to be called from blender like this:")
    print()
    print("blender --background --python render_images.py -- [args]")
    print()
    print("You can also run as a standalone python script to view all")
    print("arguments like this:")
    print()
    print("python render_images.py --help")
