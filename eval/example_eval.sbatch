#!/bin/bash
#SBATCH --job-name=MULTI
#SBATCH --cpus-per-task=
#SBATCH --gres=gpu:
#SBATCH --mem=
#SBATCH --ntasks=1
#SBATCH --partition=
#SBATCH --time=
#SBATCH --array=
#SBATCH --output=
#SBATCH --error=

echo "Start eval"

# Define common parameters
PROBLEM_FILE="../data/problem_v1.3.1_20241210_release.json"
SUBSET_LIST="../data/hard_list_v1.3.0_20241203.json"
KNOWLEDGE_FILE="../data/knowledge_v1.2.2_20240212_release.json"
#MODEL="intern-vl-2.5"
#MODEL_DIR="../models/InternVL2_5-78B"
#SPECIAL_COMMAND="--blank_image"
#MODEL="points"
#MODEL_DIR="../models/POINTS-1-5-Qwen-2-5-7B-Chat"
MODEL="qwen2-vl"
MODEL_DIR="../models/QVQ-72B-Preview"
SPECIAL_COMMAND=" --exp_name QVQ "
SAVE_EVERY=50

# Get task ID from SLURM environment variable (array task ID or manually set)
#TASK_ID=$SLURM_ARRAY_TASK_ID  # You can manually set this if not using SLURM array
TASK_ID=0  # Uncomment to manually test specific task (e.g., Task 0)

echo "Running task $TASK_ID"

# Use a case statement to define parameters for each task
case $TASK_ID in
  0)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2 --subset $SUBSET_LIST"
OUTPUT_DIR="../results"
    ;;
  1)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2"
OUTPUT_DIR="../results"
    ;;
  2)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 1,2 --input_type 1 --caption_file ../data/ocr_v1.2.0_20231217.csv --exp_name ocr"
OUTPUT_DIR="../results"
    ;;
  3)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 1,2 --input_type 1 --caption_file ../data/captions_v1.2.0_20231217.csv --exp_name cap"
OUTPUT_DIR="../results"
    ;;
  4)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 1,2 --input_type 0"
OUTPUT_DIR="../results"
    ;;
  5)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2 --knowledge_file $KNOWLEDGE_FILE --subset $SUBSET_LIST"
OUTPUT_DIR="../results"
    ;;
  6)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2 --subset $SUBSET_LIST --cot"
OUTPUT_DIR="../results_prompt"
    ;;
  7)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2 --subset $SUBSET_LIST --lang en --exp_name en"
OUTPUT_DIR="../results_prompt"
    ;;
  8)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2 --subset $SUBSET_LIST --no_background --exp_name nobk"
OUTPUT_DIR="../results_prompt"
    ;;
  9)
    TASK_PARAMS="--questions_type 0,1,2,3 --image_type 0,1,2 --input_type 2 --subset $SUBSET_LIST --no_sys --exp_name nosys"
OUTPUT_DIR="../results_prompt"
    ;;
  *)
    echo "Invalid task ID: $TASK_ID"
    exit 1
    ;;
esac

echo "Run script:"
echo "python eval.py --problem_file $PROBLEM_FILE $SPECIAL_COMMAND $TASK_PARAMS --save_every $SAVE_EVERY --model $MODEL --model_dir $MODEL_DIR --output_dir $OUTPUT_DIR"

# Run the evaluation script with the selected parameters
python eval.py \
  --problem_file $PROBLEM_FILE \
  $SPECIAL_COMMAND $TASK_PARAMS \
  --save_every $SAVE_EVERY \
  --model $MODEL \
  --model_dir $MODEL_DIR \
  --output_dir $OUTPUT_DIR

echo "Task $TASK_ID completed"
