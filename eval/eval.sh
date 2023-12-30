#!/bin/bash

# eval Qwen-VL

python eval.py --problem_file ../data/problem_v1.1.0_20231207.json --questions_type 0,1,2 --input_type 0 --model qwen-vl --cuda_device cuda:0 --model_dir QWen/Qwen-VL-Chat-Int4 
python eval.py --problem_file ../data/problem_v1.1.0_20231207.json --questions_type 0,1,2 --input_type 2 --in_turn --model qwen-vl --cuda_device cuda:0 --model_dir QWen/Qwen-VL-Chat-Int4 