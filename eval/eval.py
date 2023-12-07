"""
The Main Function of the Evaluator
"""

import os
import glob
import pdb
import sys
from args import print_model_list, parse_args_for_eval, model_list
import time
import importlib
import importlib.util
from prepare import prepare_questions
from prompts import get_prompts
import json
from tqdm import tqdm
from multiprocessing import Pool

os.environ["PYTHONPATH"] = "."


def evaluate(args, evaluator, questions):
    questions_with_answers = {}

    try:
        if args.num_workers == 1:
            for question_id, question in tqdm(questions.items()):
                questions_with_answers[question_id] = evaluator.generate_answer(question)
        else:
            with Pool(args.num_workers) as p:
                for question in tqdm(p.imap_unordered(evaluator.generate_answer, questions.values()), total=len(questions)):
                    question_id = question["question_id"]
                    questions_with_answers[question_id] = question
    except KeyboardInterrupt:
        print("Evaluation stopped by user. Previous results are saved.")  # sys.exit(0)
    except Exception as e:
        print(f"Error {e} occurred during evaluation. Previous results are saved. You can continue after checking the error.")

    os.makedirs(os.path.join(args.output_dir, args.output_name), exist_ok=True)
    with open(args.prediction_file.replace("prediction.json", "args.json"), "w", encoding="utf-8") as f:
        json.dump(vars(args), f, indent=4, ensure_ascii=False)
    with open(args.prediction_file, "w", encoding="utf-8") as f:
        json.dump(questions_with_answers, f, indent=4, ensure_ascii=False)


def generate_data(args):
    questions = prepare_questions(args)
    prompted_questions = get_prompts(questions, args)
    return prompted_questions


def get_evaluator(args):
    module_pos = f"models.{model_list[args.model]['executor']}"
    if args.use_modelscope:
        module_pos += '_ms'
    if not os.path.exists(f"models/{module_pos.split('.')[-1]}.py"):
        module_pos += "_hf"
    try:
        evaluator_module = importlib.import_module(module_pos)
        Evaluator = getattr(evaluator_module, model_list[args.model]["evaluator"])
        print(f"Using evaluator {model_list[args.model]['evaluator']} from {module_pos}")
    except:
        print(f"Module \"{model_list[args.model]['evaluator']}\" for evaluation not found in {module_pos}. Please check your implementation.")
        sys.exit(0)

    if args.model_dir:
        evaluator = Evaluator(args.model_dir, device_map=args.cuda_device)
    elif args.model_version:
        evaluator = Evaluator(api_key=args.api_key, model=args.model_version, device_map=args.cuda_device)
    else:
        evaluator = Evaluator(device_map=args.cuda_device)

    return evaluator


def check_args(args):
    time_now = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    if args.model in ["viscpm", "visualglm"] and args.input_type == 2 and not args.in_turn:
        print("Warning: viscpm model only supports one image at one time. Forced to set --in_turn to True.")
        args.in_turn = True
    if args.model in ["viscpm"] and not args.blank_image:
        print("Warning: viscpm model must have a image as input. Forced to set --black_image to True.")
        args.blank_image = True
    if args.input_type == 1 and args.caption_file is None:
        print("Warning: caption file is not specified. Switch input type to only text.")
        args.input_type = 0
    if args.num_workers > 1 and args.model_version is None:
        print("Warning: multi-processing is not supported for local models. Switching to single process.")
        args.num_workers = 1

    if not args.output_name:
        args.output_name = f"{args.exp_name + '_' if args.exp_name else ''}{args.model if not args.model_version else args.model_version}_input_{args.input_type}_shot_{args.few_shot}{'_it' if args.in_turn else ''}{'_cot' if args.cot else ''}{'_cic' if args.cap_in_cnt else ''}{'_bi' if args.blank_image else ''}_{time_now}"
    args.prediction_file = os.path.join(args.output_dir, args.output_name, "prediction.json")
    print(args)


def main(args):
    if args.model_list:
        print_model_list()
        sys.exit(0)

    if args.model not in model_list:
        print(f"The model name '{args.model}' is not in the model list. Please check the model name.")
        print_model_list()
        sys.exit(0)
    else:
        versions = model_list[args.model].get("avail_model", None)
        if versions:
            if args.model_version is None:
                args.model_version = versions[0]
            elif args.model_version not in versions:
                print(f"The model version '{args.model_version}' is not in the model list. Please check the model version.")
                print(f"Available versions: {versions}")
                sys.exit(0)

    print(f"Using model: {args.model}")
    if args.model_dir:
        print(f"Using model directory: {args.model_dir}")
    if args.model_version:
        print(f"Using model version: {args.model_version}")

    check_args(args)

    print("Generating data...")
    questions = generate_data(args)
    print("Data generated.")

    # debug mode for data generation
    if args.debug:
        exit(0)

    print(f"Loading {args.model}...")
    evaluator = get_evaluator(args)
    print(f"Model {args.model} loaded.")

    print("Evaluating...")
    evaluate(args, evaluator, questions)
    print("Evaluation finished.")


if __name__ == "__main__":
    args = parse_args_for_eval()
    args.model = args.model.lower()
    main(args)
