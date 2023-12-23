"""OpenAI GPT Evaluator"""

import google.generativeai as genai
import requests
import json
from tqdm import tqdm
import random
import time
import pdb
from utils import encode_image_PIL


class GeminiEvaluator:
    def __init__(self, api_key, model='gemini-pro', api_url=None):
        genai.configure(api_key=api_key,transport='rest')
        self.model_with_vision = genai.GenerativeModel(model_name=model)
        self.model_without_vision = genai.GenerativeModel(model_name='gemini-pro')

    def prepare_inputs(self, question):
        prompt = question["prompted_system_content"].strip() + "\n" + question["prompted_content"].strip()
        content = [prompt,]

        image_list = question.get("question_image_list")
        if image_list:
            for image_path in image_list:
                max_size = 512
                image = encode_image_PIL(image_path, max_size=max_size)
                content.append(image)
        return content

    def generate_response(self, question):
        content = self.prepare_inputs(question)
        message = None
        response = ""
        i = 0
        MAX_RETRY = 100
        while i < MAX_RETRY:
            try:
                if len(content) > 1:
                    response_ = self.model_with_vision.generate_content(content)
                    message = [content[0], ]
                    message.append(f"image no.{i+1}" for i in range(len(content) - 1))
                else:
                    response_ = self.model_without_vision.generate_content(content)
                    message = content
                response = response_.text
            except KeyboardInterrupt:
                raise Exception("Terminated by user.")
            except Exception as e:
                print(e)
                i += 1
                time.sleep(1 + i / 10)
                if i == 1 or i % 10 == 0:
                    if str(e).endswith("if the prompt was blocked."):
                        response = "Gemini refused to answer this question."
                        feedback = str(response_.prompt_feedback)
                        return response, message, feedback
                    print(f"Retry {i} times...")
            else:
                break
        if i >= MAX_RETRY:
            raise Exception("Failed to generate response.")
        return response, message, None

    def generate_answer(self, question):
        response, message, feedback = self.generate_response(question)
        question["input_message"] = message
        question["prediction"] = response
        if feedback:
            question["feedback"] = feedback
        question.pop("prompted_content")
        question.pop("prompted_system_content")
        return question
