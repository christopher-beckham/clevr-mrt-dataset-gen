
from __future__ import print_function
import math, sys, random, argparse, json, os, tempfile, string
from datetime import datetime as dt
from collections import Counter

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

  # Load the main blendfile
  bpy.ops.wm.open_mainfile(filepath="image_generation/data/street278.blend")
  bpy.ops.importgis.osm_file(filepath="export(1).osm", separate=True)
  avenues = []
  for object in bpy.context.scene.objects:
    if "Avenue" in object.name:
      avenues.append(object)
    print(object.name)
  bpy.ops.wm.save_as_mainfile(filepath="test.blend")