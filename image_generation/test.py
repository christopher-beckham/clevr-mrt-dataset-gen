import os
try:
    user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
except KeyError:
    user_paths = []

print ("paths:",user_paths)

import sys
print(sys.path)

for p in sys.path:
 print ("====",p)
 if os.path.isdir(p):
  for f in os.listdir(p):
   print (f)

import utils
print("cool")
