"""Llama2 evaluator with HuggingFace Transformers"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
import pdb

class Llama2Evaluator:
    def __init__(self, model_dir="Llama-2-13b-chat-hf", max_tokens=200, device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            "do_sample": False,
        }
        self.device_map = device_map

        self.model = AutoModelForCausalLM.from_pretrained(self.model_dir, device_map=device_map, torch_dtype=torch.float16, trust_remote_code=True).half().eval()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True)

        self.model.generation_config.__dict__.update(self.sample_params)

    def prepare_inputs(self, content_sys, content):
        content = f"<s>[INST] <<SYS>> {content_sys} <</SYS>> \n\n {{content}} [/INST]"
        return content

    def generate_response(self, question):
        message = self.prepare_inputs(question["prompted_system_content"],question["prompted_content"])
        inputs = self.tokenizer([message],add_special_tokens=False, return_tensors="pt")
        pred = self.model.generate(input_ids=inputs.input_ids[0, :4096].cuda().unsqueeze(0).to(self.device_map), eos_token_id=self.tokenizer.eos_token_id, pad_token_id=self.tokenizer.eos_token_id, **self.sample_params, )
        input_length = inputs.input_ids.size(1)
        response = self.tokenizer.decode(pred[0][input_length:], skip_special_tokens=True).strip()
        return response, message

    def generate_answer(self, question):
        response, message = self.generate_response(question)
        question["input_message"] = message
        question["prediction"] = response
        question.pop("prompted_content")
        question.pop("prompted_system_content")
        return question
