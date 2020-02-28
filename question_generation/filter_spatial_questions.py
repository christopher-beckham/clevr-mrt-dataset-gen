import os
import json

dir = "CLEVR_1.0_templates"

spatial_templates = []
all_template = []
for filename in os.listdir(dir):
    templates = json.load(open(os.path.join(dir, filename), 'r'))
    for template in templates:
        for statement in template['text']:
            if "<R>" in statement:
                spatial_templates.append(template)
                break
json.dump(templates, open("CLEVR_KIWI_SPATIAL/templates.json", 'w'))