"""Qwen2VL evaluator with HuggingFace Transformers"""

from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from transformers.generation import GenerationConfig
import re
import pdb
import torch
from qwen_vl_utils import process_vision_info
from utils import encode_image_base64


class Qwen2VLEvaluator:
    def __init__(self, model_dir="Qwen/Qwen2-VL-7B-Instruct",  # "Qwen/Qwen-VL-Chat"
                 max_tokens=2000, device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            "do_sample": False
        }

        if "AWQ" in model_dir:
            # self.model = Qwen2VLForConditionalGeneration.from_pretrained(self.model_dir, torch_dtype="auto", device_map="auto")
            # self.model = Qwen2VLForConditionalGeneration.from_pretrained(self.model_dir, torch_dtype=torch.float16, device_map="auto", use_cache=False)
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(self.model_dir, torch_dtype=torch.float16, attn_implementation="flash_attention_2", device_map="auto", use_cache=False).eval()
        else:
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(self.model_dir, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2", device_map="auto").eval()
        max_pixels = 1280 * 28 * 28
        self.processor = AutoProcessor.from_pretrained(self.model_dir, max_pixels=max_pixels)

    def prepare_inputs(self, question):
        image_list = question.get("image_list")
        messages = [{
            "role": "system",
            "content": question["prompted_system_content"]
        }]
        messages_str = []

        if image_list:
            user_message = {
                "role": "user",
                "content": []}
            for image_path in image_list:
                base64_image = encode_image_base64(image_path)  #
                user_message["content"].append({
                    "type": "image",
                    "image": f"data:image/png;base64,{base64_image}",
                })
                messages_str.append(f"data:image/png;base64,{base64_image}"[:64])
            user_message["content"].append({
                "type": "text",
                "text": question["prompted_content"]
            })
            messages.append(user_message)
        else:
            messages.append({
                "role": "user",
                "content": question["prompted_content"]
            }, )

        text_input = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        messages_str.append(text_input)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text_input],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to("cuda")

        return inputs, messages_str

    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            inputs, message = self.prepare_inputs(question)
            generated_ids = self.model.generate(**inputs, max_new_tokens=2000,temperature=0.1)
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
            response= self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
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
