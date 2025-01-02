"""
Generate image captions using the Blip2 model.
"""

import torch
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import sys
import os
from tqdm import tqdm
import random
import pdb
from transformers import AutoModelForCausalLM, AutoTokenizer
from wepoints.utils.images import Qwen2ImageProcessorForPOINTSV15
import torch
import pdb
device = torch.device("cuda") if torch.cuda.is_available() else "cpu"


class POINTSEvaluator:
    def __init__(self, model_dir='WePOINTS/POINTS-1-5-Qwen-2-5-7B-Chat', max_tokens=2000):
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
    
    def get_image_caption(self, image_path):
        message = [{
            'role': 'user',
            'content': [{
                'type': 'image',
                'image': image_path
            },
            {
                'type': 'text',
                'text': 'Question: Please describe the image as detailed as possible. Answer:'
            }]
        }]
        
        response = self.model.chat(message, self.tokenizer, self.image_processor, self.sample_params).replace('\n', ' ')
        return response
    
    def get_image_ocr(self, image_path):
        message = [{
            'role': 'user',
            'content': [{
                'type': 'image',
                'image': image_path
            }, {
                'type': 'text',
                'text': 'Question: Please provide the OCR content of the image. If there is no OCR content, please type "No OCR content". Answer:'
            }]
        }]
        
        response = self.model.chat(message, self.tokenizer, self.image_processor, self.sample_params).replace('\n', ' ')
        return response

if __name__ == '__main__':
    image_dir = '../data/images'
    caption_path = '../data/captions_v1.3.1_20241210_points.csv'
    caption_data = open(caption_path, 'w', encoding='utf-8')
    # ocr_path = '../data/ocr_v1.3.1_20241210_points.csv'
    # ocr_data = open(ocr_path, 'w', encoding='utf-8')

    prompt = None # 'Question: Please describe the image as detailed as possible. Answer:'

    points_model = POINTSEvaluator('../models/POINTS-1-5-Qwen-2-5-7B-Chat', max_tokens=2000)

    image_list = []

    # walk through the image directory
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith(".png"):
                image_list.append(os.path.join(root, file))

    for image_path in tqdm(image_list):
        caption_data.write(image_path + ',' + points_model.get_image_caption(image_path) + '\n')
        caption_data.flush()
        # ocr_data.write(image_path + ',' + points_model.get_image_ocr(image_path) + '\n')

    caption_data.close()
    # ocr_data.close()
