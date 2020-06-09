import os
import json

dir = "CLEVR_1.0_templates"
total_num = 0
spatial_num = 0
all_template = []
for filename in os.listdir(dir):
    templates = json.load(open(os.path.join(dir, filename), 'r'))
    spatial_templates = []
    for template in templates:
        total_num += 1
        for statement in template['text']:
            if "<R>" in statement:
                spatial_num += 1
                spatial_templates.append(template)
                break
    json.dump(spatial_templates, open(f"CLEVR_KIWI_SPATIAL/{filename}", 'w'))
print(f"total_num: {total_num}")
print(f"spatial_num: {spatial_num}")
