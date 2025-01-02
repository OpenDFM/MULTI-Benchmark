"""Qwen2VL evaluator with HuggingFace Transformers"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import re
import pdb
import torch


class Qwen2Evaluator:
    def __init__(self, model_dir="Qwen/Qwen2-7B-Instruct", max_tokens=200, device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            "do_sample": False
        }
        
        self.model = AutoModelForCausalLM.from_pretrained(self.model_dir, torch_dtype="auto", attn_implementation="flash_attention_2", device_map=device_map, trust_remote_code=True).eval().cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True)
    
    def prepare_inputs(self, question):
        messages = [{
            "role": "system",
            "content": question["prompted_system_content"]
        }, {
            "role": "user",
            "content": question["prompted_content"]
        }]
        
        text_input = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        model_inputs = self.tokenizer([text_input], return_tensors="pt").to("cuda")
        
        return model_inputs, text_input
    
    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            inputs, message = self.prepare_inputs(question)
            generated_ids = self.model.generate(inputs.input_ids, max_new_tokens=500)
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            response = self.tokenizer.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
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
            pdb.set_trace()
            response = ""
            torch.cuda.empty_cache()
        question["prediction"] = response
        return question
