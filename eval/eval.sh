#!/bin/bash

python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --questions_type 0,1,2,3 \
     --input_type 0 \
     --model llama2 \
     --model_dir ../models/dfm-2.0-13b \
     --cuda_device cuda:5 \
     --exp_name dfm-2.0-13b

python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --knowledge_file ../data/knowledge_v1.2.0_20231217.json \
     --questions_type 0,1,2,3 \
     --input_type 0 \
     --model llama2 \
     --model_dir ../models/dfm-2.0-13b \
     --cuda_device cuda:6 \
     --exp_name dfm-2.0-13b


python eval.py --checkpoint_dir ../results/dfm-2.0-13b_llama2_input_0_shot_0_kn_20240125_191329