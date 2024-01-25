"""VisualCPM Evaluator with HuggingFace Transformers"""

import os
import pdb
import re
from VisCPM import VisCPMChat
from utils import open_image

# os.environ["CUDA_MEMORY_CPMBEE_MAX"] = "8g"  # Low VRAM support but slower


class VisCPMEvaluator():
    def __init__(self, model_dir="../../data/models/VisCPM-Chat", max_tokens=200, temperature=0.1, top_p=0.9, **kwargs):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        self.model = VisCPMChat(os.path.join(self.model_dir, 'pytorch_model.v1.bin'), image_safety_checker=False)

    def prepare_inputs(self, content):
        match = re.findall("<img_[0-9]+>", content)
        for img_sub in match:
            content = content.replace(img_sub, '[IMAGE]')
        content = content.replace("<", "<<")
        return content

    def generate_response(self, input):
        # Here we make a high-level understanding of `generate_response`
        if isinstance(input, dict):
            # question with <=1 image
            question = input
            image_path = question.get("image_list", [""])[0]
            image = open_image(image_path)
            message = self.prepare_inputs(question["prompted_content"])
            response, _, _ = self.model.chat(image, message)
            return response, message
        elif isinstance(input, tuple):
            # question with multiple images
            assert len(input) == 4, "Input tuple must have 4 elements. (prompt, image_path, context, history)"
            message, image_path, context, history = input
            image = open_image(image_path)
            message = self.prepare_inputs(message)
            response, context, history = self.model.chat(image, message, context, history)
            return response, context, history, message
        else:
            raise ValueError(f"Input type not supported: {type(input)}")

    def generate_answer(self, question):
        if question.get("prompted_content"):
            assert len(question.get("image_list", [""])) <= 1, "VisCPM model only supports one image at one time."
            response, message = self.generate_response(question)
            question["input_message"] = message
            question.pop("prompted_content")
        elif question.get("prompted_content_list"):
            # Processing questions with multiple images in a model of seemingly 1-image support is essential.
            # We consider multiple-rounds chat to send images separately,
            prompted_content_list = question.get("prompted_content_list")
            image_list = question.get("image_list").copy()
            # image_list.append("")
            context, history = "", None
            assert len(prompted_content_list) == len(image_list), f"Length of prompted_content_list and image_list must be the same. \n{question}"
            question["answer_history"] = []
            question["input_message_list"] = []
            for multi_rounds_prompt, image_path in zip(prompted_content_list, image_list):
                response, context, history, message = self.generate_response((multi_rounds_prompt, image_path, context, history))
                question["answer_history"].append(response)
                question["input_message_list"].append(message)
            question.pop("prompted_content_list")
        else:
            raise ValueError(f"Question not supported: {question}")
        question["prediction"] = response
        return question
