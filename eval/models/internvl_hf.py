"""InternVL Evaluator with HuggingFace Transformers"""

from transformers import AutoTokenizer, AutoModel, CLIPImageProcessor
import torch
from PIL import Image


class InternVLEvaluator():
    def __init__(self, model_dir="OpenGVLab/InternVL-Chat-Chinese-V1-1", device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": 512,
            "do_sample": False,
            "num_beams": 1,
        }

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.image_processor = CLIPImageProcessor.from_pretrained(self.model_dir)
        self.model = AutoModel.from_pretrained(self.model_dir, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True, trust_remote_code=True, device_map=device_map).eval()

        # self.model.generation_config.__dict__.update(self.sample_params)

    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            image_path = question.get("image_list", [""])[0]
            image = Image.open(image_path).convert('RGB')
            image = image.resize((448, 448))
            pixel_values = self.image_processor(images=image, return_tensors='pt').pixel_values
            pixel_values = pixel_values.to(torch.bfloat16).cuda()
            message = question["prompted_content"]
            response, _ = self.model.chat(self.tokenizer, pixel_values, message, None, **self.sample_params)
            return response, message

        elif isinstance(input, tuple):
            # question with multiple images
            assert len(input) == 3, "Input tuple must have 3 elements. (prompt, image_path, history)"
            message, image_path, history = input
            image = Image.open(image_path).convert('RGB')
            image = image.resize((448, 448))
            pixel_values = self.image_processor(images=image, return_tensors='pt').pixel_values
            pixel_values = pixel_values.to(torch.bfloat16).cuda()
            response, history = self.model.chat(self.tokenizer, pixel_values, message, history, **self.sample_params)
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
            image_list = question.get("image_list").copy()
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
