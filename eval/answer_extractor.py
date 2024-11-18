"""
Extract answers from the output of the o1 model
"""

import json
import pdb

from tqdm import tqdm
from prompts import answer_extractor_prompt
from models.gpt import GPTEvaluator
from args import parse_args_for_answer_extractor

def extract_answer(model,pred):
    """
    Extract answers from the output of the o1 model
    """

    messages = [{
        "role": "system",
        "content":  answer_extractor_prompt
    },{
        "role": "system",
        "content":  pred
    }
    ]

    pred_extract = model.generate_response(messages,prepare_inputs=False)

    return pred_extract

def main(args):
    with open(args.prediction_file, 'r', encoding="utf-8") as f:
        pred_data = json.load(f)

    model=GPTEvaluator(api_key=args.api_key, model=args.model_version, api_url=args.api_url, max_tokens=500, temperature=0, top_p=1, presence_penalty=0.0, frequency_penalty=0.0)

    for pred in tqdm(pred_data.keys()):
        pred_extract=extract_answer(model,pred_data[pred]["prediction"])
        pred_data[pred]["prediction"]=[pred_extract, pred_data[pred]["prediction"]]

    with open(args.prediction_file.replace(".json", "_extracted.json"), 'w', encoding="utf-8") as f:
        json.dump(pred_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    args = parse_args_for_answer_extractor()
    main(args)