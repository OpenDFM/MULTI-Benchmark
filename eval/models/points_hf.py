"""POINTS evaluator with HuggingFace Transformers"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from wepoints.utils.images import Qwen2ImageProcessorForPOINTSV15
import torch
import pdb


class POINTSEvaluator:
    def __init__(self, model_dir='WePOINTS/POINTS-1-5-Qwen-2-5-7B-Chat', max_tokens=2000, device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            'temperature': 0.0,
            'top_p': 0.0,
            'num_beams': 1,
        }
        
        self.model = AutoModelForCausalLM.from_pretrained(self.model_dir, trust_remote_code=True, torch_dtype=torch.float16, device_map='cuda')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True)
        self.image_processor = Qwen2ImageProcessorForPOINTSV15.from_pretrained(self.model_dir)
    
    def prepare_inputs(self, question):
        image_list = question.get("image_list",[]   )
        messages = []
        
        user_message = {
            "role": "user",
            "content": []
        }
        if len(image_list) > 0:
            image_list=["../data/placeholder_black.png"]
        for image_path in image_list:
            user_message["content"].append({
                "type": "image",
                "image": image_path,
            })
        user_message["content"].append({
            "type": "text",
            "text": question["prompted_content"]
        })
        messages.append(user_message)
        
        return messages
    
    
    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            message = self.prepare_inputs(question)
            response = self.model.chat(message, self.tokenizer, self.image_processor, self.sample_params)
            return response, message
        elif isinstance(input, tuple):
            raise ValueError(f"input type not supported: {type(input)}")
        else:
            raise ValueError(f"input type not supported: {type(input)}")
    
    def generate_answer(self, question):
        try:
            if question.get("prompted_content"):
                response, message = self.generate_response(question)
                question["input_message"] = message
                question.pop("prompted_content")
            else:
                raise ValueError(f"Question not supported: {question}")
        except Exception as e:
            print(e)
            response = ""
            torch.cuda.empty_cache()
        question["prediction"] = response
        return question
