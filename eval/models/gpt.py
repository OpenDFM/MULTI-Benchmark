"""OpenAI GPT Evaluator"""

from openai import OpenAI
import requests
import json
from tqdm import tqdm
import random
import time
import pdb
from utils import encode_image_base64
from args import api_price


class GPTEvaluator():
    def __init__(self, api_key, model='gpt-4o', api_url="https://api.openai.com/v1/chat/completions", max_tokens=500, temperature=0.1, top_p=1, presence_penalty=0.0, frequency_penalty=0.0):
        self.api_key = api_key
        self.api_url = api_url
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.post_dict = {
            "model": model,
            "messages": None,
            "max_tokens": 32768,
            
            # "temperature": temperature,
            # "top_p": top_p,
            # "presence_penalty": presence_penalty,
            # "frequency_penalty": frequency_penalty,
        }
        self.tokens = {
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        self.tokens_this_run = {
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        self.price = api_price.get(model, [0.005, 0.015])
        self.timeout = 3600
        self.proxies = {
            "http": None,
            "https": None,
        }
    
    def calculate_usage(self, response):
        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"].get("completion_tokens", 0)
        self.tokens["prompt_tokens"] += prompt_tokens
        self.tokens["completion_tokens"] += completion_tokens
        self.tokens_this_run["prompt_tokens"] += prompt_tokens
        self.tokens_this_run["completion_tokens"] += completion_tokens
        # print(f"Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}, Cost: ${'{0:.5f}'.format(prompt_tokens / 1000 * self.price[0] + completion_tokens / 1000 * self.price[1])}")
        return prompt_tokens, completion_tokens
    
    def calculate_usage_total(self):
        print(f"Total prompt tokens: {self.tokens['prompt_tokens']}, Total completion tokens: {self.tokens['completion_tokens']}, Total cost: ${'{0:.5f}'.format(self.tokens['prompt_tokens'] / 1000 * self.price[0] + self.tokens['completion_tokens'] / 1000 * self.price[1])}")
    
    def prepare_inputs(self, question):
        image_list = question.get("image_list")
        if question["prompted_system_content"]:
            messages = [{
                "role": "system",
                "content": question["prompted_system_content"]
            }]
        else:
            messages = []
        
        if image_list:
            user_message = {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": question["prompted_content"]
                }, ]
            }
            for image_path in image_list:
                base64_image = encode_image_base64(image_path)  #
                user_message["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "auto"
                    },
                }, )
            messages.append(user_message)
        else:
            messages.append({
                "role": "user",
                "content": question["prompted_content"]
            }, )
        
        return messages
    
    def generate_response(self, question, prepare_inputs=True):
        if prepare_inputs:
            message = self.prepare_inputs(question)
        else:
            message = question
        self.post_dict["messages"] = message
        response = ""
        response_ = None
        i = 0
        MAX_RETRY = 10
        while i < MAX_RETRY:
            try:
                response_ = requests.post(self.api_url, json=self.post_dict, headers=self.header, proxies=self.proxies, timeout=self.timeout)
                response_ = response_.json()
                response = response_["choices"][0]["message"]["content"]
                # print(response_)
                self.calculate_usage(response_)
            except KeyboardInterrupt:
                raise Exception("Terminated by user.")
            except Exception as e:
                # return "", message, ""
                print(f"Error: {e}")
                print(response_)
                error = ""
                try:
                    error = response_["error"]["message"].split("(request id:")[0].strip()
                    print(error)
                    print(response_.json())
                except:
                    pass
                i += 1
                time.sleep(1 + i / 10)
                if i == 1 or i % 10 == 0:
                    if error.startswith("This model's maximum context length") or error.startswith("Your input image may contain") or error.startswith("The response was filtered"):
                        response = ""
                        feedback = error
                        return response, message, feedback
                    print(f"Retry {i} times...")
            else:
                break
        if i >= MAX_RETRY:
            raise Exception("Failed to generate response.")
        return response, message, None
    
    def generate_answer(self, question):
        response, message, feedback = self.generate_response(question)
        if not isinstance(message[-1]["content"], str):
            for i in range(len(message[-1]["content"])):
                if message[-1]["content"][i]["type"] == "image_url":
                    message[-1]["content"][i]["image_url"]["url"] = message[-1]["content"][i]["image_url"]["url"][:64] + "..."
        question["input_message"] = message
        question["prediction"] = response
        if feedback:
            question["feedback"] = feedback
        question.pop("prompted_content")
        question.pop("prompted_system_content")
        question["prompt_tokens"] = self.tokens_this_run["prompt_tokens"]
        question["completion_tokens"] = self.tokens_this_run["completion_tokens"]
        self.tokens_this_run = {
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        return question
