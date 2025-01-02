"""MiniCPM-V Evaluator with HuggingFace Transformers"""

import os
import pdb
import re
from utils import open_image

import torch
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer


class MiniCPMEvaluator():
    def __init__(self, model_dir='../../models/MiniCPM-V-2_6', max_tokens=2000, temperature=0.1, top_p=0.9,device_map="auto", **kwargs):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        print(f'Loading model from {self.model_dir}')
        self.model = AutoModel.from_pretrained(self.model_dir, trust_remote_code=True)
        self.model = self.model.to(dtype=torch.float16)

        if torch.cuda.device_count() > 1:
            print(f"Using {torch.cuda.device_count()} GPUs for parallel processing")
            self.model = torch.nn.DataParallel(self.model)

        self.model = self.model.eval().cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True, _attn_implementation="flash_attention_2")
        torch.cuda.empty_cache()

    def prepare_inputs(self, question):
        image_list = question.get("image_list",[])


        if image_list:
            content = []
            content_str=[]
            for image_path in image_list:
                image = open_image(image_path)
                content.append(image)
                content_str.append(str(image))
            content.append(question["prompted_content"])
            content_str.append(question["prompted_content"])

            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
            message_str=[{
                    "role": "user",
                    "content": content_str
                }]

        else:
            messages = [{
                "role": "user",
                "content": [question["prompted_content"]]
            }]
            message_str= messages

        return messages,message_str

    def generate_response(self, question):
        messages,message_str = self.prepare_inputs(question)
        res = self.model.chat(
            image=None,
            msgs=messages,
            context=None,
            tokenizer=self.tokenizer,
            **self.sample_params
        )
        if isinstance(res, tuple) and len(res) > 0:
            res = res[0]
        return res,message_str

    def generate_answer(self, question):
        response, message = self.generate_response(question)
        question["input_message"] = message
        question.pop("prompted_content")
        question["prediction"] = response
        return question
