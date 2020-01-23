# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

import sys, random, os
import bpy, bpy_extras


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
  # import pdb; pdb.set_trace()

  bpy.context.scene.objects.active = bpy.data.objects[new_name]
  bpy.context.object.rotation_euler[2] = theta
  bpy.ops.transform.resize(value=(scale, scale, scale))
  bpy.ops.transform.translate(value=(x, y, scale))


# def setup_dev():
#   # Do this to ensure that we can access these files in blender
#   # echo $PWD/image_generation >> /home/martin/blender-2.78c-linux-glibc219-x86_64/2.78/python/lib/python3.5/site-packages/clevr.pth
#   #  ~/.local/bin/blender/blender
#   # Imports
#   bpy.ops.wm.open_mainfile(filepath="data/base_scene.blend")
#   import utils
#   import bmesh
#   from mathutils import Vector
#
#   utils.load_materials("data/materials")
#
#   # add a cube
#   #utils.add_object("data/shapes", "SmoothCube_v2", 0.7, (0, 0), theta=20.)
#   utils.add_object("data/shapes", "SmoothCylinder", 0.7, (0, 0), theta=20.)
#   cube = bpy.data.objects['SmoothCube_v2_0']
#
#   bpy.ops.object.mode_set(mode='OBJECT')
#   cam_loc = bpy.data.objects["Camera"].location
#   (hit, loc, norm, face_index) = cube.closest_point_on_mesh(cam_loc) # https://blender.stackexchange.com/questions/58409/how-do-i-find-the-closest-point-on-another-mesh-to-a-vertex-with-python
#
#
#   bpy.ops.object.text_add(location=loc)
#   text = bpy.data.objects['Text']
#   text.data.body = "Hallo"
#   text.data.extrude = 0.03
#   text.rotation_euler = (1.5, 0, 1.0)
#   m = text.new('My SubDiv', 'SUBSURF')
#   m.levels = 1
#   m.render_levels = 2
#   m.subdivision_type = "SIMPLE"
#
#
#   # shrink wrap the text to the object
##
#   # load fonts
#
#   # load text dataset (w/ entities?)
#
#   # randomize text sizes, styles and locations on the objects
#
#
#
#   # Excess crap
#   # myFontCurve = bpy.data.curves.new(type="FONT", name="myFontCurve")
#   # myFontOb = bpy.data.objects.new("myFontOb", myFontCurve)
#   # myFontOb.data.body = "my text"
#   # bpy.context.scene.objects.link(myFontOb)
#   # bpy.context.scene.update()
#   # vert_list = [cube.matrix_world * v.co for v in cube.data.vertices]
#   # face_verts = [cube.matrix_world * v.co for v in bm.faces[0]]
#
#   # Ensure we are in edit mode and get a bmesh / bbox of the cube
#   # bpy.ops.object.mode_set(mode='EDIT')
#   # bpy.ops.mesh.normals_make_consistent(inside=False)
#   # bm = bmesh.from_edit_mesh(cube.data)
#   # bbox = [x[:] for x in cube.bound_box]


def add_text(body):
  obj = bpy.context.active_object
  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.context.active_object.modifiers['Subsurf'].levels = 2  # View
  bpy.context.active_object.modifiers['Subsurf'].render_levels = 2  # Render
  bpy.context.active_object.modifiers['Subsurf'].subdivision_type = "SIMPLE"

  # TODO: center align text instead of this
  text_location = obj.location.copy()
  # text_location[0] = text_location[0] - .29 * obj.dimensions[0]
  # text_location[1] = text_location[1] - .29 * obj.dimensions[1]
  # bpy.context.scene.update()

  bpy.ops.object.text_add(location=text_location)
  text = bpy.context.active_object
  text.data.body = body
  text.data.extrude = 0.03
  text.data.size = 0.3
  text.data.align_x = "CENTER"

  # load and set font
  font_dir = "data/fonts"
  font = random.choice(os.listdir(font_dir))
  font_path = os.path.join(font_dir, font)
  font = bpy.data.fonts.load(font_path)
  text.data.font = font

  bpy.context.scene.update()
  if text.dimensions[0] > obj.dimensions[0]:
    text.dimensions[0] = obj.dimensions[0] - 0.3
  if text.dimensions[1] > obj.dimensions[1]:
    text.dimensions[1] = obj.dimensions[1] - 0.1
  bpy.context.scene.update()

  bpy.ops.object.modifier_add(type='SUBSURF')
  bpy.context.active_object.modifiers['Subsurf'].levels = 2  # View
  bpy.context.active_object.modifiers['Subsurf'].render_levels = 2  # Render
  bpy.context.active_object.modifiers['Subsurf'].subdivision_type = "SIMPLE"

  # Split Text into characters. TODO: Throw out any words containing seperated
  # bpy.ops.object.convert(target="MESH")
  # bpy.ops.object.mode_set(mode='EDIT')
  # bpy.ops.mesh.select_all(action='SELECT')
  # bpy.ops.mesh.separate(type='LOOSE')
  # bpy.ops.object.mode_set(mode='OBJECT')

  bpy.ops.object.modifier_add(type='SHRINKWRAP')
  bpy.context.active_object.modifiers['Shrinkwrap'].target = obj
  bpy.context.active_object.modifiers['Shrinkwrap'].offset = 0.01
  bpy.context.active_object.modifiers['Shrinkwrap'].wrap_method = "PROJECT"
  bpy.context.active_object.modifiers['Shrinkwrap'].use_project_z = True

  text.rotation_euler = (1.5, 0, 1.0)

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

