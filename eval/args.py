"""
Argparsers for eval and score.
"""

import argparse

model_list = {
    "gpt-4v": {
        "model_type": "api",
        "support_input": [0, 1, 2, 3],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
    },
    "gpt": {
        "avail_model": ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-4", "gpt-4-0314", "gpt-4-0613", ],
        "model_type": "api",
        "support_input": [0, 1],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
    },
    "moss": {
        "model_type": "local",
        "support_input": [0, 1],
        "executor": "moss",
        "evaluator": "MOSSEvaluator",
    },
    "viscpm": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "viscpm",
        "evaluator": "VisCPMEvaluator",
    },
    "qwen-vl": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "qwen",
        "evaluator": "QwenEvaluator",
    },
    "llava": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "llava",
        "evaluator": "LLaVAEvaluator",
    },
    "minigpt-4": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "minigpt4",
        "evaluator": "miniGPT4Evaluator",
    },
    "visualglm": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "visualglm",
        "evaluator": "VisualGLMEvaluator",
    },
    "visualcla": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "visualcla",
        "evaluator": "VisualCLAEvaluator",
    },
}


def parse_args_for_eval():
    parser = argparse.ArgumentParser()

    # data setting
    parser.add_argument('--problem_file', type=str, default=None, help='Specify the input question json file.')
    parser.add_argument('--knowledge_file', type=str, default=None, help='Specify the knowledge json file.')
    parser.add_argument('--caption_file', type=str, default=None, help='Specify the image caption csv file.')
    parser.add_argument('--output_dir', type=str, default='../results', help='Specify the main output directory.')
    parser.add_argument('--output_name', type=str, default=None, help='Specify the output sub directory name. By leaving it empty, it will be automatically generated.')
    parser.add_argument('--exp_name', type=str, default=None, help='Add the experiment name prefix to the output name.')

    # model setting
    parser.add_argument('--model', '-m', type=str, default=None, help='Specify the model name.')
    parser.add_argument('--model_version', '-v', type=str, default=None, help='Specify the model type. You need to fill in this if you want to test specific model version.')
    parser.add_argument('--model_dir', '-d', type=str, default=None, help='Specify the model directory. You need to fill in this if you want to test those models that are deployed locally.')
    parser.add_argument('--cuda_device', '-c', type=str, default='cpu', help='Specify the cuda device. By leaving it empty, it means using cpu. You can specify multiple cuda devices by separating them with commas, i.e. "0,1,2,3".')
    parser.add_argument('--api_key', type=str, default=None, help='Specify the api key. You need to fill in this if you want to test those models that are not deployed locally.')

    # whether to use modelscope.
    # Note. In SOME regions where huggingface repos are not easily accessed, modelscope provides an alternative.
    parser.add_argument('--use_modelscope', action='store_true', help="whether to use modelscope")

    # eval setting
    parser.add_argument('--in_turn', action="store_true", help='Whether to use in-turn input for multi-image questions. If not, the model will receive all the images at once.')
    parser.add_argument('--cot', action='store_true', help='Whether to use chain-of-thought.')
    parser.add_argument('--few_shot', '-k', type=int, default=0, help='Specify the number of few shot samples. By leaving it empty, it means zero-shot k=0.')
    parser.add_argument('--questions_type', type=str, default="0,1,2",
        help='Specify the type of the questions to be tested. 0 - single_choice, 1 - multiple_choices, 2 - fill_in_the_blank, 3 - discussion_questions. By leaving it empty, it means subjective questions [0,1,2].')
    parser.add_argument('--subset', type=str, default=None, help='A file to the list of the problems to be tested.')
    parser.add_argument('--subject', type=str, default=None, help='Specify the subject of the problems to be tested.')
    parser.add_argument('--input_type', type=int, choices=range(0, 4), default=0, help='Specify the input type. 0 - only_text, 1 - text_with_captions, 2 - text_and_images, 3 - only_images. By leaving it empty, it means only_text.')
    parser.add_argument('--eval_num', type=int, default=-1, help='Specify the number of the problems to be tested. By leaving it empty, all the problems available will be evaluated.')
    parser.add_argument('--random', action='store_true', help='Whether to randomly select the problems to be tested.')
    parser.add_argument('--num_workers', '-n', type=int, default=1, help='Specify the number of the threads when using api.')

    # detail eval setting
    parser.add_argument('--cap_in_cnt', action='store_true', help='Whether to include the image caption in the content or list after the problem content.')
    parser.add_argument('--lang', type=str, default='zh', choices=['zh', 'en'], help='Specify the language of the prompt content.')
    parser.add_argument('--blank_image', action="store_true", help='If the input type is 2, whether to use blank image as the placeholder for the image.')

    # other functions
    parser.add_argument('--model_list', '-l', action='store_true', help='Print the available model list.')
    parser.add_argument('--debug', action='store_true', help='If you only want to test data generation.')

    args = parser.parse_args()
    return args


def parse_args_for_score():
    parser = argparse.ArgumentParser()

    # data setting
    parser.add_argument('--label_file', type=str, default=None, help='Specify the label json file.')
    parser.add_argument('--prediction_file', type=str, default=None, help='Specify the prediction json file.')
    parser.add_argument('--score_file', type=str, default=None, help='Specify the output detail score file.')
    parser.add_argument('--reference_dir', type=str, default=None, help='Specify the reference directory where all the other score files are stored. By leaving it empty, only absolute score will be calculated.')

    # score setting
    parser.add_argument('--detail', action='store_true', help='Whether to print the detail of the score.')
    parser.add_argument('--only_past', action='store_true', help='Whether to only use the earlier models to calculate the relative score.')

    # other functions
    parser.add_argument('--model_list', '-l', action='store_true', help='Print the available model list.')

    args = parser.parse_args()
    return args


def print_model_list():
    for model_name in model_list:
        print(model_name)
        print(model_list[model_name])
        versions = model_list[model_name].get("avail_model", [])
        if len(versions) > 0:
            print(f"Available versions: {versions}")
        print()
    print(model_list)
