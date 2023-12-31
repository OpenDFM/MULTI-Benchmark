"""OpenAI GPT Evaluator"""

from openai import OpenAI
import requests
import json
from tqdm import tqdm
import random
import time
import pdb
from utils import encode_image_base64


class GPTEvaluator:
    def __init__(self, api_key, model='gpt-3.5-turbo', api_url="https://api.openai.com/v1/chat/completions", max_tokens=500, temperature=0.1, top_p=1, presence_penalty=0.0, frequency_penalty=0.0):
        self.api_key = api_key
        self.api_url = api_url
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.post_dict = {
            "model": model,
            "messages": None,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }

    def prepare_inputs(self, question):
        image_list = question.get("question_image_list")
        messages = [{
            "role": "system",
            "content": question["prompted_system_content"]
        }]

        if image_list:
            user_message = {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": question["prompted_content"]
                },]}
            for image_path in image_list:
                max_size = 512
                base64_image, origin_pixels = encode_image_base64(image_path, max_size=max_size)
                detail = "high" if origin_pixels > max_size * max_size / 2 else "low"
                user_message["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": detail,  # "auto"
                    },},)
            messages.append(user_message)
        else:
            messages.append({
                "role": "user",
                "content": question["prompted_content"]
            }, )

        return messages

    def generate_response(self, question):
        message = self.prepare_inputs(question)
        self.post_dict["messages"] = message
        response = ""
        response_ = None
        i = 0
        MAX_RETRY = 100
        while i < MAX_RETRY:
            try:
                response_ = requests.post(self.api_url, json=self.post_dict, headers=self.header)
                response_ = response_.json()
                response = response_["choices"][0]["message"]["content"]
            except KeyboardInterrupt:
                raise Exception("Terminated by user.")
            except Exception:
                print(response_)
                try:
                    print(response_.json())
                except:
                    pass
                i += 1
                time.sleep(1 + i / 10)
                if i == 1 or i % 10 == 0:
                    print(f"Retry {i} times...")
            else:
                break
        if i >= MAX_RETRY:
            raise Exception("Failed to generate response.")
        return response, message

    def generate_answer(self, question):
        response, message = self.generate_response(question)
        question["input_message"] = message
        question["prediction"] = response
        question.pop("prompted_content")
        question.pop("prompted_system_content")
        return question
