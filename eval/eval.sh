#!/bin/bash

export CUDA_VISIBLE_DEVICES=3,4,5,6,7
python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --knowledge_file ../data/knowledge_v1.2.0_20231217.json \
     --questions_type 0,1,2,3 \
     --input_type 0 \
     --model dfm \
     --model_dir ../models/dfm-2.0-70b \
     --cuda_device auto

python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --caption_file ../data/captions_v1.2.0_20231217.csv \
     --questions_type 0,1,2,3 \
     --input_type 1 \
     --model dfm \
     --model_dir ../models/dfm-2.0-70b \
     --cuda_device auto

python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --caption_file ../data/ocr_v1.2.0_20231217.csv \
     --questions_type 0,1,2,3 \
     --input_type 1 \
     --model dfm \
     --model_dir ../models/dfm-2.0-70b \
     --cuda_device auto

export CUDA_VISIBLE_DEVICES=0
python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --questions_type 0,1,2,3 \
     --input_type 0 \
     --model dfm \
     --model_dir ../models/dfm-2.0-13b \
     --cuda_device auto

export CUDA_VISIBLE_DEVICES=1
python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --caption_file ../data/captions_v1.2.0_20231217.csv \
     --questions_type 0,1,2,3 \
     --input_type 1 \
     --model dfm \
     --model_dir ../models/dfm-2.0-13b \
     --cuda_device auto

export CUDA_VISIBLE_DEVICES=2
python eval.py \
     --problem_file ../data/problem_v1.2.0_20231217.json \
     --caption_file ../data/ocr_v1.2.0_20231217.csv \
     --questions_type 0,1,2,3 \
     --input_type 1 \
     --model dfm \
     --model_dir ../models/dfm-2.0-13b \
     --cuda_device auto
