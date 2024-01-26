"""VisualGLM Evaluator with ModelScope"""

from modelscope import snapshot_download, AutoTokenizer, AutoModel
import torch
from typing import List, Dict, Union, Tuple, Any
import re
from os import PathLike
from prompts import CoT_identifier


class VisualGLMEvaluator():
    def __init__(self, model_path="ZhipuAI/visualglm-6b", revision="v1.0.3", max_tokens=8192, device_map="cuda:0"):
        self.model_path = model_path
        self.sample_params = {
            "max_length": max_tokens,
            "do_sample": False,
        }

        model_path = snapshot_download(model_path, revision=revision)

        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        if not hasattr(self.tokenizer, "model_dir"):
            self.tokenizer.model_dir = model_path
        self.model = (AutoModel.from_pretrained(model_path, device_map=device_map, trust_remote_code=True, ).half().eval())  # 18G VRAM without quantize. May need optimization

        self.model.generation_config.__dict__.update(self.sample_params)

    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            image_path = question.get("image_list", [""])[0]
            message = question["prompted_content"]
            response, _ = self.model.chat(self.tokenizer, image_path, message, None, **self.sample_params)
            return response, message

        elif isinstance(input, tuple):
            # question with multiple images
            assert len(input) == 3, "Input tuple must have 3 elements. (prompt, image_path, history)"
            message, image_path, history = input
            response, history = self.model.chat(self.tokenizer, image_path, message, history, **self.sample_params)
            return response, history, message
        else:
            raise ValueError(f"input type not supported: {type(input)}")

    def generate_answer(self, question):
        if question.get("prompted_content"):
            assert len(question.get("image_list", [""])) <= 1, "VisualGLM model only supports one image at one time."
            response, message = self.generate_response(question)
            question["input_message"] = message
            question.pop("prompted_content")
        elif question.get("prompted_content_list"):
            # Processing questions with multiple images in a model of seemingly 1-image support is essential.
            # We consider multiple-rounds chat to send images separately,
            prompted_content_list = question.get("prompted_content_list")
            image_list = question.get("image_list")
            # image_list.append("")
            history = None
            assert len(prompted_content_list) == len(image_list), f"Length of prompted_content_list and image_list must be the same. \n{question}"
            question["answer_history"] = []
            question["input_message_list"] = []
            for multi_rounds_prompt, image_path in zip(prompted_content_list, image_list):
                response, history, message = self.generate_response((multi_rounds_prompt, image_path, history))
                question["answer_history"].append(response)
                question["input_message_list"].append(message)
            question.pop("prompted_content_list")
        else:
            raise ValueError(f"Question not supported: {question}")
        question["prediction"] = response
        return question
