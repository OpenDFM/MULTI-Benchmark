import json
import os

json_path = '../../MULTI-Benchmark/results/gemini-pro_input_0_shot_0_20231223_141324/prediction.json'
json_path_add = '../../MULTI-Benchmark/results/gemini-pro-vision_input_2_shot_0_20231224_004723/prediction.json'
json_path_output = '../../MULTI-Benchmark/results/gemini-pro-vision_input_2_shot_0_20231224_004723/add_no_image/prediction.json'

os.makedirs(os.path.dirname(json_path_output), exist_ok=True)

with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

with open(json_path_add, 'r', encoding='utf-8') as f:
    json_data_add = json.load(f)

print(len(json_data))
print(len(json_data_add))

for item in json_data_add:
    json_data[item] = json_data_add[item]

with open(json_path_output, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)
