"""
Argparsers for eval and score.
"""

import argparse

model_list = {
    "gpt-4o": {
        "avail_model": ["gpt-4o-2024-08-06","gpt-4o-2024-05-13", "gpt-4o","gpt-4o-mini","gpt-4o-mini-2024-07-18","o1-preview-2024-09-12","o1-mini-2024-09-12","gpt-4o-2024-11-20","gpt-4.1","gpt-4.1-mini","gpt-4.1-nano"],
        "model_type": "api",
        "support_input": [0, 1, 2, 3],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
        "split_sys": True,
    },
    "gpt-4v": {
        "avail_model": ["gpt-4-vision-preview"],
        "model_type": "api",
        "support_input": [2, 3],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
        "split_sys": True,
    },
    "gpt": {
        "avail_model": ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-1106-preview"],
        "model_type": "api",
        "support_input": [0, 1],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
        "split_sys": True,
    },
    "claude-api": {
        "avail_model": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-5-sonnet-20241022"],
        "model_type": "api",
        "support_input": [0, 1, 2, 3],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
        "split_sys": True,
    },
    "gemini-api": {
        "avail_model": ["gemini-1.5-pro-latest","gemini-1.5-flash-latest"],
        "model_type": "api",
        "support_input": [0, 1, 2, 3],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
        "split_sys": True,
    },
    "step-api": {
        "avail_model": ["step-1v-8k","step-1v-32k"],
        "model_type": "api",
        "support_input": [0, 1, 2, 3],
        "executor": "gpt",
        "evaluator": "GPTEvaluator",
        "split_sys": True,
    },
    "claude": {
        "avail_model": ["claude-3-opus-20240229", "claude-3-sonnet-20240229","claude-3-5-sonnet-20241022"],
        "model_type": "api",
        "support_input": [0, 1, 2, 3],
        "executor": "claude",
        "evaluator": "ClaudeEvaluator",
        "split_sys": True,
    },
    "geminivision": {
        "avail_model": ["gemini-pro-vision", ],
        "model_type": "api",
        "support_input": [2, 3],
        "executor": "gemini",
        "evaluator": "GeminiEvaluator",
        "split_sys": True,
    },
    "gemini": {
        "avail_model": ["gemini-pro", ],
        "model_type": "api",
        "support_input": [0, 1],
        "executor": "gemini",
        "evaluator": "GeminiEvaluator",
        "split_sys": True,
    },
    "moss": {
        "model_type": "local",
        "support_input": [0, 1],
        "executor": "moss",
        "evaluator": "MOSSEvaluator",
        "split_sys": False,
    },
    "viscpm": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "viscpm",
        "evaluator": "VisCPMEvaluator",
        "split_sys": False,
    },
    "minicpmv": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "minicpmv",
        "evaluator": "MiniCPMEvaluator",
        "split_sys": False,
    },
    "qwen-vl": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "qwenvl",
        "evaluator": "QwenVLEvaluator",
        "split_sys": False,
    },
    "qwen2-vl": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "qwen2vl",
        "evaluator": "Qwen2VLEvaluator",
        "split_sys": True,
    },
    "qwen2.5-vl": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "qwen25vl",
        "evaluator": "Qwen2_5VLEvaluator",
        "split_sys": True,
    },
    "qwen2": {
        "model_type": "local",
        "support_input": [0, 1],
        "executor": "qwen2",
        "evaluator": "Qwen2Evaluator",
        "split_sys": True,
    },
    "points": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "points",
        "evaluator": "POINTSEvaluator",
        "split_sys": False,
    },
    "visualglm": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "visualglm",
        "evaluator": "VisualGLMEvaluator",
        "split_sys": False,
    },
    "llama2": {
        "model_type": "local",
        "support_input": [0, 1],
        "executor": "llama2",
        "evaluator": "Llama2Evaluator",
        "split_sys": True,
    },
    "dfm": {
        "model_type": "local",
        "support_input": [0, 1],
        "executor": "dfm",
        "evaluator": "DFMEvaluator",
        "split_sys": True,
    },
    "intern-vl": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "internvl",
        "evaluator": "InternVLEvaluator",
        "split_sys": False,
    },
    "intern-vl-2": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "internvl2",
        "evaluator": "InternVLEvaluator",
        "split_sys": False,
    },
    "intern-vl-2.5": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "internvl2",
        "evaluator": "InternVLEvaluator",
        "split_sys": False,
    },
    "internlm": {
        "model_type": "local",
        "support_input": [0, 1],
        "executor": "internlm",
        "evaluator": "InternLMEvaluator",
        "split_sys": False,
    },
    "human": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "human",
        "evaluator": "HumanEvaluator",
        "split_sys": True,
    },
    "deepseek-vl2": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "deepseekvl2",
        "evaluator": "DeepSeekVL2Evaluator",
        "split_sys": False,
    },
    "deepseek-janus": {
        "model_type": "local",
        "support_input": [0, 1, 2, 3],
        "executor": "deepseekjanus",
        "evaluator": "DeepSeekJanusEvaluator",
        "split_sys": False,
    },
}


api_price= { # The price of the model per 1k tokens, [input, output], USD
    "gpt-4-vision-preview": [0.01,0.03],
    "gpt-3.5-turbo-0125":[0.0005,0.0015],
    "gpt-4.1": [0.002,0.008],
    "gpt-4.1-mini": [0.0004,0.0016],
    "gpt-4.1-nano": [0.0001,0.0004],
    "gpt-4o": [0.005,0.015],
    "gpt-4o-2024-11-20": [0.0025,0.01],
    "gpt-4o-2024-08-06": [0.0025,0.01],
    "gpt-4o-mini": [0.00015,0.0006],
    "gpt-4o-mini-2024-07-18": [0.00015,0.0006],
    "o1-mini-2024-09-12": [0.006,0.018],
    "o1-preview-2024-09-12": [0.03,0.09],
    "gemini-1.5-pro-latest": [0.00125,0.005],
    "gemini-1.5-flash-latest": [0.000075,0.00025],
    "gemini-1.5-flash-exp-0827": [0.000075,0.00025],
    "glm-4v-plus": [0.01,0.01], # CNY
    "glm-4v": [0.05,0.05], # CNY
    "claude-3-5-sonnet-20241022": [0.005,0.010],
    "step-1v-8k": [0.000667,0.0033], # CNY
    "step-1v-32k": [0.002,0.010], # CNY
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
    parser.add_argument('--checkpoint_dir', type=str, default=None, help='Specify the checkpoint directory. You need to fill in this if you want to continue unfinished evaluation.')

    # model setting
    parser.add_argument('--model', '-m', type=str, default=None, help='Specify the model name.')
    parser.add_argument('--model_version', '-v', type=str, default=None, help='Specify the model type. You need to fill in this if you want to test specific model version for GPTs.')
    parser.add_argument('--model_dir', '-d', type=str, default=None, help='Specify the model directory. You need to fill in this if you want to test those models that are deployed locally.')
    parser.add_argument('--cuda_device', '-c', type=str, default='auto', help='Specify the cuda device. By leaving it empty, it means using auto. You can specify multiple cuda devices by separating them with commas, i.e. "0,1,2,3".')
    parser.add_argument('--api_key', type=str, default=None, help='Specify the api key. You need to fill in this if you want to test those models that are not deployed locally.')
    parser.add_argument('--api_url', type=str, default="https://api.openai.com/v1/chat/completions", help='Specify the api url. You need to fill in this if you want to test those models that are not deployed locally.')

    # whether to use modelscope.
    # Note. In SOME regions where huggingface repos are not easily accessed, modelscope provides an alternative.
    parser.add_argument('--use_modelscope', action='store_true', help="whether to use modelscope")

    # eval setting
    parser.add_argument('--in_turn', action="store_true", help='Whether to use in-turn input for multi-image questions. If not, the model will receive all the images at once. This argument is only valid to the models that support multi-image input.')
    parser.add_argument('--cot', action='store_true', help='Whether to use chain-of-thought. The performance using chain-of-thought is not guaranteed.')
    parser.add_argument('--no_background', action='store_true', help='Whether to add the background information to the prompt.')
    parser.add_argument('--no_sys', action='store_true', help='Whether to use system prompt.')
    parser.add_argument('--few_shot', '-k', type=int, default=0, help='Specify the number of few shot samples. By leaving it empty, it means zero-shot k=0. The performance using few-shot is not guaranteed.')
    parser.add_argument('--questions_type', type=str, default="0,1,2",
                        help='Specify the type of the questions to be tested. 0 - single-answer choosing (SA), 1 - multiple-answer choosing (MA), 2 - fill-in-the-blank (FB), 3 - discussion-questions (OP). By leaving it empty, it means subjective questions [0,1,2].')
    parser.add_argument('--image_type', type=str, default="0,1,2",
                        help='Specify the number images involved in the questions to be tested. 0 - no-image (NI), 1 - single-image (SI), 2 - multiple-image (MI). By leaving it empty, it means all questions [0,1,2].')
    parser.add_argument('--subset', type=str, default=None, help='The path to the list of the problems to be tested. Use "../data/hard_list_v1.2.1_20240206.json" to test on MULTI-Elite.')
    parser.add_argument('--subject', type=str, default=None, help='Specify the subject of the problems to be tested.')
    parser.add_argument('--input_type', type=int, choices=range(0, 4), default=0, help='Specify the input type. 0 - pure-text, 1 - text-with-captions/ocr, 2 - text-and-images, 3 - only-images. By leaving it empty, it means pure_text.')
    parser.add_argument('--eval_num', type=int, default=-1, help='Specify the number of the problems to be tested. By leaving it empty, all the problems available will be evaluated.')
    parser.add_argument('--random', action='store_true', help='Whether to randomly select the problems to be tested.')
    parser.add_argument('--num_workers', '-n', type=int, default=1, help='Specify the number of the threads when using api. Eval gemini with multiple threads may not work properly.')
    parser.add_argument('--save_every', type=int, default=100, help='Save the results every n questions. Set to -1 to save only at the end.')

    # detail eval setting
    parser.add_argument('--cap_in_cnt', action='store_true', help='Whether to include the image caption in the content or list after the problem content.')
    parser.add_argument('--lang', type=str, default='zh', choices=['zh', 'en'], help='Specify the language of the prompt content. The performance using english prompt is not guaranteed.')
    parser.add_argument('--blank_image', action="store_true", help='Whether to use blank image as the placeholder for the image. This argument is only valid when the input type is 2.')

    # other functions
    parser.add_argument('--model_list', '-l', action='store_true', help='Print the available model list.')
    parser.add_argument('--debug', action='store_true', help='If you only want to test data generation.')

    args = parser.parse_args()
    return args


def parse_args_for_answer_extractor():
    parser = argparse.ArgumentParser()

    parser.add_argument('--prediction_file', type=str, default=None, help='Specify the prediction json file.')
    parser.add_argument('--model_version', '-v', type=str, default="gpt-4o-mini", help='Specify the model type. You need to fill in this if you want to test specific model version for GPTs.')
    parser.add_argument('--api_key', type=str, default=None, help='Specify the api key. You need to fill in this if you want to test those models that are not deployed locally.')
    parser.add_argument('--api_url', type=str, default="https://api.openai.com/v1/chat/completions", help='Specify the api url. You need to fill in this if you want to test those models that are not deployed locally.')

    args = parser.parse_args()
    return args


def parse_args_for_score():
    parser = argparse.ArgumentParser()

    # data setting
    parser.add_argument('--label_file', type=str, default=None, help='Specify the label json file.')
    parser.add_argument('--prediction_file', type=str, default=None, help='Specify the prediction json file.')
    parser.add_argument('--score_file', type=str, default=None, help='Specify the output detail score file.')
    parser.add_argument('--reference_file', type=str, default=None, help='Specify the reference prediction json file.')
    parser.add_argument('--reference_dir', type=str, default=None, help='Specify the reference directory where all the other score files are stored. By leaving it empty, only absolute score will be calculated.')

    # score setting
    parser.add_argument('--detail', action='store_true', help='Whether to print the detail of the score.')
    parser.add_argument('--answer_position',type=str,choices=['start','end'],default='start',help='Specify the position of the answer to be evaluated. If you are evaluating o1 models or CoT setting, you should set this to "end".')
    parser.add_argument('--only_past', action='store_true', help='Whether to only use the earlier models to calculate the relative score.')

    # other functions
    parser.add_argument('--model_list', '-l', action='store_true', help='Print the available model list.')

    args = parser.parse_args()
    return args


def parse_args_for_score_deploy():
    class Args:
        pass
    
    # data setting
    args = Args()
    
    args.label_file = None
    args.prediction_file = None
    args.score_file = None
    args.reference_file = None
    args.reference_dir = None

    # score setting
    args.detail = False
    args.only_past = False
    args.answer_position = 'start'

    # other functions
    args.model_list = False

    return args


def print_model_list():
    print('=' * 20)
    for model_name in model_list:
        print(f'[{model_name}]')
        print('  ', model_list[model_name])
        # versions = model_list[model_name].get("avail_model", [])
        # if len(versions) > 0:
        #     print(f"Available versions: {versions}")
        # print()
    # print(model_list)
    print('=' * 20)
