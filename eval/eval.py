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
import tiktoken

os.environ["PYTHONPATH"] = "."


def evaluate(args, evaluator, questions):
    questions_with_answers = questions
    questions_with_no_answers = {}

    for question_id, question in questions.items():
        if not question.get("prediction"):
            questions_with_no_answers[question_id] = question

    print(f"Total number of questions: {len(questions_with_no_answers)}")

    try:
        if args.num_workers == 1:
            for question_id, question in tqdm(questions_with_no_answers.items()):
                questions_with_answers[question_id] = evaluator.generate_answer(question)
        else:
            with Pool(args.num_workers) as p:
                for question in tqdm(p.imap_unordered(evaluator.generate_answer, questions_with_no_answers.values()), total=len(questions_with_no_answers)):
                    question_id = question["question_id"]
                    questions_with_answers[question_id] = question
    except KeyboardInterrupt:
        print("Evaluation stopped by user. Previous results are saved.")  # sys.exit(0)
    except Exception as e:
        print(f"Error {e} occurred during evaluation. Previous results are saved. You can continue after checking the error.")

    os.makedirs(os.path.join(args.output_dir, args.output_name), exist_ok=True)
    args_json=vars(args)
    args_json.pop("api_key")
    with open(args.prediction_file.replace("prediction.json", "args.json"), "w", encoding="utf-8") as f:
        json.dump(args_json, f, indent=4, ensure_ascii=False) # we don't want to save the api key in file
    with open(args.prediction_file, "w", encoding="utf-8") as f:
        json.dump(questions_with_answers, f, indent=4, ensure_ascii=False)


def generate_data(args):
    questions = prepare_questions(args)
    prompted_questions = get_prompts(questions, args)

    # calculate the number of tokens
    if args.model_version:
        encoding = tiktoken.encoding_for_model(args.model_version)
    else:
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-0613')
    input_token_num = 0
    input_image_num = 0
    for question_id, question in tqdm(prompted_questions.items()):
        input_token_num += len(encoding.encode(question.get("prompted_system_content", "")))+len(encoding.encode(question.get("prompted_user_content", "")))+len(encoding.encode(question.get("prompted_content", "")))+len(encoding.encode(" ".join(question.get("prompted_content_list", []))))
        input_image_num += question["question_image_number"]

    print(f"Total number of tokens: {input_token_num}")
    print(f"Total number of images: {input_image_num}")
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
        evaluator = Evaluator(api_url=args.api_url,api_key=args.api_key, model=args.model_version)
    else:
        evaluator = Evaluator(device_map=args.cuda_device)

    return evaluator


def check_args(args):
    time_now = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    if args.model in ["viscpm", "visualglm"] and args.input_type == 2 and not args.in_turn:
        print("Warning: viscpm model only supports one image at one time. Forced to set --in_turn to True.")
        args.in_turn = True
    if args.model in ["gpt-4v"] and args.input_type == 2 and args.in_turn:
        print("Warning: do not support multi-turn input since it's quite expensive and there is rate limit. Forced to set --in_turn to False.")
        args.in_turn = False
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

    if args.checkpoint_dir:
        print(f"Continuing evaluation from {args.checkpoint_dir}")
        # load args from checkpoint
        with open(os.path.join(args.checkpoint_dir, "args.json"), "r", encoding="utf-8") as f:
            args.__dict__.update(json.load(f))
        print(f"Loaded args from checkpoint")
        print(args)

        questions = json.load(open(os.path.join(args.prediction_file), "r", encoding="utf-8"))
    else:
        args.model = args.model.lower()
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

        if args.input_type not in model_list[args.model]["support_input"]:
            print(f"The input type '{args.input_type}' is not supported by the model '{args.model}'. Please check the input type.")
            print(f"Supported input types: {model_list[args.model]['support_input']}")
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
            # print(questions)
            exit(0)

    print(f"Loading {args.model}...")
    evaluator = get_evaluator(args)
    print(f"Model {args.model} loaded.")

    print("Evaluating...")
    evaluate(args, evaluator, questions)
    print("Evaluation finished.")

if __name__ == "__main__":
    args = parse_args_for_eval()
    main(args)
