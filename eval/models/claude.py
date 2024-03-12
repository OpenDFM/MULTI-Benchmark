"""Anthropic Claude Evaluator"""

import httpx
from anthropic import Anthropic
import requests
import json
from tqdm import tqdm
import random
import time
import pdb
from utils import encode_image_base64
import re


class ClaudeEvaluator:
    def __init__(self, api_key, model='claude-3-opus-20240229', api_url=None, max_tokens=200, temperature=0.1, top_p=1, presence_penalty=0.0, frequency_penalty=0.0,use_client=False):
        self.use_client =use_client
        self.api_key = api_key
        self.api_url = api_url
        if self.use_client:
            self.client = Anthropic(api_key=self.api_key ,base_url=self.api_url) # http_client=httpx.Client(proxies=api_url, transport=httpx.HTTPTransport(local_address="0.0.0.0"))
        else:
            self.header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            self.post_dict = {
                "model": model,
                "system": None,
                "messages": None,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty,
            }
        self.model = model

    def prepare_inputs(self, question):
        image_list = question.get("image_list")
        prompted_content = question["prompted_content"]
        if image_list:
            match = re.findall("\[IMAGE_[0-9]+]", prompted_content)
            assert len(match) == len(image_list)
            content = []
            for i, img_sub in enumerate(match):
                img_token_start = prompted_content.index(img_sub)
                prompted_content_split = prompted_content[:img_token_start].strip() + f" Image {i + 1}:"
                content.append({
                    "type": "text",
                    "text": prompted_content_split
                })
                prompted_content = prompted_content[img_token_start + len(img_sub):]

                base64_image = encode_image_base64(image_list[i])  # max_size = 512
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64_image,
                    },
                })
            content.append({
                "type": "text",
                "text": prompted_content
            })

        else:
            content = [{
                "type": "text",
                "text": prompted_content
            }]

        return content

    def generate_response(self, question):
        content = self.prepare_inputs(question)
        messages = [{
            "role": "user",
            "content": content
        }]
        system_message = question["prompted_system_content"]
        if not self.use_client:
            self.post_dict["system"] = system_message
            self.post_dict["messages"] = messages

        response = ""
        i = 0
        MAX_RETRY = 100

        while i < MAX_RETRY:
            try:
                if self.use_client:
                    response_ = self.client.messages.create(model=self.model, system=system_message, messages=messages)
                    response = response_  # THIS HAS NOT BEEN VERIFIED
                else:
                    response_ = requests.post(self.api_url, json=self.post_dict, headers=self.header)
                    response_ = response_.json()
                    response = response_["choices"][0]["message"]["content"]
            except KeyboardInterrupt:
                raise Exception("Terminated by user.")
            except Exception as e:
                print(e)
                i += 1
                time.sleep(1 + i / 10)
                if i == 1 or i % 10 == 0:
                    error_type = response_.get("error", {}).get("type", "")
                    if error_type == 'upstream_error':
                        response = ""
                        feedback = error_type
                        return response, [system_message, messages], feedback
                    print(f"Retry {i} times...")
            else:
                break
        if i >= MAX_RETRY:
            raise Exception("Failed to generate response.")
        return response, [system_message, messages], None

    def generate_answer(self, question):
        response, message_, feedback = self.generate_response(question)
        message = {
            "system": message_[0],
            "messages": message_[1]
        }
        for i in range(len(message["messages"][0]["content"])):
            if message["messages"][0]["content"][i]["type"] == "image":
                message["messages"][0]["content"][i]["source"]["data"] = message["messages"][0]["content"][i]["source"]["data"][:32] + "..."
        question["input_message"] = message
        question["prediction"] = response
        if feedback:
            question["feedback"] = feedback
        question.pop("prompted_content")
        question.pop("prompted_system_content")
        return question
