# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import sys, random, os, math
import bpy, bpy_extras
import numpy as np
from mathutils import Vector
import collections
from bpy_extras.object_utils import world_to_camera_view
"""
Some utility functions for interacting with Blender
"""


def extract_args(input_argv=None):
  """
  Pull out command-line arguments after "--". Blender ignores command-line flags
  after --, so this lets us forward command line arguments from the blender
  invocation to our own script.
  """
  if input_argv is None:
    input_argv = sys.argv
  output_argv = []
  if '--' in input_argv:
    idx = input_argv.index('--')
    output_argv = input_argv[(idx + 1):]
  return output_argv


def parse_args(parser, argv=None):
  return parser.parse_args(extract_args(argv))


# I wonder if there's a better way to do this?
def delete_object(obj):
  """ Delete a specified blender object """
  for o in bpy.data.objects:
    o.select = False
  obj.select = True
  bpy.ops.object.delete()


def bounds(cam, obj, local=False):

  local_coords = obj.bound_box[:]
  om = obj.matrix_world

  if not local:
    worldify = lambda p: om * Vector(p[:])
    coords = [worldify(p).to_tuple() for p in local_coords]
  else:
    coords = [p[:] for p in local_coords]
  cam_coords = []

  for coord in coords:
    cam_coords.append(get_camera_coords(cam, Vector(coord)))

  return cam_coords


def get_camera_coords(cam, pos):
  """
  For a specified point, get both the 3D coordinates and 2D pixel-space
  coordinates of the point from the perspective of the camera.

  Inputs:
  - cam: Camera object
  - pos: Vector giving 3D world-space position

  Returns a tuple of:
  - (px, py, pz): px and py give 2D image-space coordinates; pz gives depth
    in the range [-1, 1]
  """
  scene = bpy.context.scene
  x, y, z = bpy_extras.object_utils.world_to_camera_view(scene, cam, pos)
  scale = scene.render.resolution_percentage / 100.0
  w = int(scale * scene.render.resolution_x)
  h = int(scale * scene.render.resolution_y)
  px = int(round(x * w))
  py = int(round(h - y * h))
  return (px, py, z)


def set_layer(obj, layer_idx):
  """ Move an object to a particular layer """
  # Set the target layer to True first because an object must always be on
  # at least one layer.
  obj.layers[layer_idx] = True
  for i in range(len(obj.layers)):
    obj.layers[i] = (i == layer_idx)


def add_object(object_dir, name, scale, loc, theta=0):
  """
  Load an object from a file. We assume that in the directory object_dir, there
  is a file named "$name.blend" which contains a single object named "$name"
  that has unit size and is centered at the origin.

  - scale: scalar giving the size that the object should be in the scene
  - loc: tuple (x, y) giving the coordinates on the ground plane where the
    object should be placed.
  """
  # First figure out how many of this object are already in the scene so we can
  # give the new object a unique name
  count = 0
  for obj in bpy.data.objects:
    if obj.name.startswith(name):
      count += 1

  filename = os.path.join(object_dir, '%s.blend' % name, 'Object', name)
  bpy.ops.wm.append(filename=filename)

  # Give it a new name to avoid conflicts
  new_name = '%s_%d' % (name, count)
  bpy.data.objects[name].name = new_name

  # Set the new object as active, then rotate, scale, and translate it
  x, y = loc

  bpy.context.scene.objects.active = bpy.data.objects[new_name]
  bpy.context.object.rotation_euler[2] = theta
  bpy.ops.transform.resize(value=(scale, scale, scale))
  bpy.ops.transform.translate(value=(x, y, scale))

def make_invisible(ob):
  for child in ob.children:
    child.hide = True
    # call the function on the child to catch all its children
    # as there is no ob.children_recursive attribute
    make_invisible(child)

def make_visible(ob):
  for child in ob.children:
    child.hide = False
    # call the function on the child to catch all its children
    # as there is no ob.children_recursive attribute
    make_visible(child)

def load_font(text):
  # load and set font
  font_dir = "data/fonts"
  font = random.choice(os.listdir(font_dir))
  font_path = os.path.join(font_dir, font)
  font = bpy.data.fonts.load(font_path)
  text.data.font = font


def add_text(body, random_rotation, cams):
  # Take the current object and "increase the resolution"
  obj = bpy.context.active_object
  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.context.active_object.modifiers['Subsurf'].levels = 2  # View
  bpy.context.active_object.modifiers['Subsurf'].render_levels = 2  # Render
  bpy.context.active_object.modifiers['Subsurf'].subdivision_type = "SIMPLE"

  # Create the text at the location where the object is
  loc = obj.location.copy()
  loc[2] = loc[2] - 0.2
  bpy.ops.object.text_add(location=loc)
  text = bpy.context.active_object
  text.data.body = body
  text.data.extrude = 0.0
  text.data.size = 1.0#0.5
  text.data.align_x = "CENTER"
  bpy.context.scene.update()

  # Increase text mesh resolution and rotate
  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.context.active_object.modifiers['Subsurf'].levels = 3  # View
  bpy.context.active_object.modifiers['Subsurf'].render_levels = 3  # Render
  bpy.context.active_object.modifiers['Subsurf'].subdivision_type = "SIMPLE"

  bpy.ops.object.modifier_add(type='SHRINKWRAP')
  bpy.context.active_object.modifiers['Shrinkwrap'].target = obj
  bpy.context.active_object.modifiers['Shrinkwrap'].offset = 0.01
  bpy.context.active_object.modifiers['Shrinkwrap'].wrap_method = "PROJECT"
  bpy.context.active_object.modifiers['Shrinkwrap'].use_project_z = True
  bpy.context.active_object.modifiers['Shrinkwrap'].use_project_x = True
  bpy.context.active_object.modifiers['Shrinkwrap'].use_positive_direction = True
  bpy.context.active_object.modifiers['Shrinkwrap'].use_negative_direction = False
  if random_rotation:
    rot = random.random() * math.pi
  else:
    rot = random.random() * -0.5

  text.rotation_euler = (1.5, 0, rot)
  bpy.context.scene.update()

  # copy the existing text then break into characters
  bpy.ops.object.duplicate()
  bpy.ops.object.convert(target="MESH")
  bpy.ops.object.mode_set(mode='EDIT')
  bpy.ops.mesh.select_all(action='SELECT')
  bpy.ops.mesh.separate(type='LOOSE')
  bpy.ops.object.mode_set(mode='OBJECT')
  bpy.context.scene.update()

  chars = bpy.context.selected_objects
  bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
  bpy.context.scene.objects.active = text
  make_invisible(text)

  if len(chars) != len(text.data.body):
    print("wrong number of meshes")
    raise Exception

  char_bboxes = {cam.name: [] for cam in cams}
  word_bboxes = {cam.name: [] for cam in cams}
  for cam in cams:
    for i, o in enumerate(chars):
      bbox_coords = bounds(cam, o)
      o_loc = get_camera_coords(cam, o.location)
      char_bboxes[cam.name].append({"center": o_loc, "bbox": bbox_coords, "id": o.data.name, 'visible_pixels': 0})
      make_invisible(o)
    char_bboxes[cam.name] = id_chars(text, char_bboxes[cam.name])
    word_bboxes[cam.name] = make_scale_word_bbox(char_bboxes[cam.name])
  make_visible(text)
  text.data.extrude = 0.03

  return word_bboxes, char_bboxes, chars

def make_scale_word_bbox(text):
  min_x = 99999
  min_y = 99999
  max_x = 0.
  max_y = 0.
  for char in text:
    for x, y, z in  char['bbox']:
      if x < min_x:
        min_x = x
      if x > max_x:
        max_x = x
      if y < min_y:
        min_y = y
      if y > max_y:
        max_y = y
  min_x = min_x / bpy.context.scene.render.resolution_x
  min_y = min_y / bpy.context.scene.render.resolution_y
  max_x = max_x / bpy.context.scene.render.resolution_x
  max_y = max_y / bpy.context.scene.render.resolution_y
  w = max_x - min_x
  h = max_y - min_y
  return min_x, min_y, w, h

def id_chars(text, char_bboxes):
  # currently assumes script is written left to right
  bbox_dict = {bbox['center'][0]:bbox for bbox in char_bboxes}
  ltr = sorted([bbox['center'][0] for bbox in char_bboxes])
  for i, k in enumerate(ltr):
    bbox_dict[k]['char'] = text.data.body[i]
  return list(bbox_dict.values())

def load_materials(material_dir):
  """
  Load materials from a directory. We assume that the directory contains .blend
  files with one material each. The file X.blend has a single NodeTree item named
  X; this NodeTree item must have a "Color" input that accepts an RGBA value.
  """
  for fn in os.listdir(material_dir):
    if not fn.endswith('.blend'): continue
    name = os.path.splitext(fn)[0]
    filepath = os.path.join(material_dir, fn, 'NodeTree', name)
    bpy.ops.wm.append(filename=filepath)

def cartesian_to_spherical(cam_x, cam_y, cam_z):
  # keep in mind that we're in a right-hand rule system, i.e. z is up, x-y is the floor
  xy = cam_x ** 2 + cam_y ** 2  # ground-projected radius
  distance = np.sqrt(xy + cam_z ** 2)
  elevation = np.arctan2(cam_z, np.sqrt(xy))
  azimuth = np.arctan2(cam_y, cam_x)
  return distance, elevation, azimuth


def add_material(name, **properties):
  """
  Create a new material and assign it to the active object. "name" should be the
  name of a material that has been previously loaded using load_materials.
  """
  # Figure out how many materials are already in the scene
  mat_count = len(bpy.data.materials)

  # Create a new material; it is not attached to anything and
  # it will be called "Material"
  bpy.ops.material.new()

  # Get a reference to the material we just created and rename it;
  # then the next time we make a new material it will still be called
  # "Material" and we will still be able to look it up by name
  mat = bpy.data.materials['Material']
  mat.name = 'Material_%d' % mat_count

  # Attach the new material to the active object
  # Make sure it doesn't already have materials
  obj = bpy.context.active_object
  assert len(obj.data.materials) == 0
  obj.data.materials.append(mat)

  # Find the output node of the new material
  output_node = None
  for n in mat.node_tree.nodes:
    if n.name == 'Material Output':
      output_node = n
      break

  # Add a new GroupNode to the node tree of the active material,
  # and copy the node tree from the preloaded node group to the
  # new group node. This copying seems to happen by-value, so
  # we can create multiple materials of the same type without them
  # clobbering each other
  group_node = mat.node_tree.nodes.new('ShaderNodeGroup')
  group_node.node_tree = bpy.data.node_groups[name]

  # Find and set the "Color" input of the new group node
  for inp in group_node.inputs:
    if inp.name in properties:
      inp.default_value = properties[inp.name]

  # Wire the output of the new group node to the input of
  # the MaterialOutput node
  mat.node_tree.links.new(
      group_node.outputs['Shader'],
      output_node.inputs['Surface'],
  )

