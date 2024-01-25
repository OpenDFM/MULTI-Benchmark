#!/bin/bash
# for model in glm; do 
for folder in ../results_on_hard/*; do
    echo $(realpath $folder)
    python metrics.py --label_file ../data/problem_v1.2.0_20231217.json --detail --prediction_file ${folder}/prediction.json
done
for folder in ../results_on_hard/*/add_no_image; do
    echo $(realpath $folder)
    python metrics.py --label_file ../data/problem_v1.2.0_20231217.json --detail --prediction_file ${folder}/prediction.json
done
# done

# python metrics.py --label_file ../data/problem_v1.1.0_20231207.json --detail --prediction_file