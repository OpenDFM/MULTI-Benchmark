"""OpenAI GPT Evaluator"""

import openai
import requests
import json
from tqdm import tqdm
import random
import time
import pdb


class GPTEvaluator:
    def __init__(self, api_key, model='gpt-3.5-turbo', api_url="https://frostsnowjh.com/v1/chat/completions", max_tokens=120, temperature=0.1, top_p=1, presence_penalty=0.0, frequency_penalty=0.0, request_timeout=10.0):
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
            "request_timeout": request_timeout,
        }

    def prepare_inputs(self, question):
        messages = [{
            "role": "system",
            "content": question["prompted_system_content"]
        }, {
            "role": "user",
            "content": question["prompted_content"]
        }, ]
        return messages

    def generate_response(self, question):
        message = self.prepare_inputs(question)
        self.post_dict["messages"] = message
        response = ""
        response_ = None
        i = 0
        while i < 100:
            try:
                response_ = requests.post(self.api_url, json=self.post_dict, headers=self.header)
                response_ = response_.json()
                response = response_["choices"][0]["message"]["content"]
            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                # print(e)
                # print(self.post_dict)
                # print(self.header)
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
        # TODO: add more robust retry mechanism
        return response, message

    def generate_answer(self, question):
        response, message = self.generate_response(question)
        question["input_message"] = message
        question["prediction"] = response
        question.pop("prompted_content")
        question.pop("prompted_system_content")
        return question
