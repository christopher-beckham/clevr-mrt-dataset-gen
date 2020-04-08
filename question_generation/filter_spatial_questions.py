import os
import json

dir = "CLEVR_1.0_templates"

all_template = []
for filename in os.listdir(dir):
    templates = json.load(open(os.path.join(dir, filename), 'r'))
    spatial_templates = []
    for template in templates:
        print(template)
        for statement in template['text']:
            if "<R>" in statement:
                spatial_templates.append(template)
                break
    json.dump(spatial_templates, open(f"CLEVR_KIWI_SPATIAL/{filename}", 'w'))