#!/bin/bash
for folder in gpt-4-vision-preview_input_2_shot_0_20231221_101231/add_no_image qwen-vl_input_2_shot_0_it_20231225_083611 gemini-pro-vision_input_2_shot_0_20231224_004723/add_no_image moss_input_0_shot_0_20231226_070654 gemini-pro_input_0_shot_0_20231223_141324 gpt-3.5-turbo-0613_input_0_shot_0_20231220_143731 viscpm_input_2_shot_0_it_bi_20231228_194002 gpt-4-1106-preview_input_0_shot_0_20231220_214000; do
    python extract_response_on_hard.py -j ../data/selected_hard_list_20231229.json -i $folder
done