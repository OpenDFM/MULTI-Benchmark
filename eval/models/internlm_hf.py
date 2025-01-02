"""InternLM2.5 Evaluator with HuggingFace Transformers"""

import pdb
import torch
from transformers import AutoModel, AutoTokenizer


class InternLMEvaluator():
    def __init__(self, model_dir="internlm/internlm2_5-7b-chat", device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": 512,
            "do_sample": False,
            "num_beams": 3,
        }

        self.tokenizer =AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True, use_fast=False)
        self.model = AutoModel.from_pretrained(self.model_dir, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map=device_map).eval().cuda()

    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            content=question["prompted_content"]
            response, history = self.model.chat(self.tokenizer, content, history=[])
            return response, content

        elif isinstance(input, tuple):
            raise ValueError(f"input type not supported: {type(input)}")
        else:
            raise ValueError(f"input type not supported: {type(input)}")

    def generate_answer(self, question):
        if question.get("prompted_content"):
            response, message = self.generate_response(question)
            question["input_message"] = message
            question.pop("prompted_content")
        elif question.get("prompted_content_list"):
            raise ValueError(f"Question not supported: {question}")
        else:
            raise ValueError(f"Question not supported: {question}")
        question["prediction"] = response
        return question
