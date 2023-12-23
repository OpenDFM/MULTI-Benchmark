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
device = torch.device("cuda") if torch.cuda.is_available() else "cpu"


class ImageCaptioner:
    def __init__(self, model_path='Salesforce/blip2-opt-6.7b', load_in_8bit=False, prompt=None):
        self.processor = Blip2Processor.from_pretrained(model_path)
        if load_in_8bit:
            self.model = Blip2ForConditionalGeneration.from_pretrained(model_path, load_in_8bit=True, device_map="auto")
        else:
            self.model = Blip2ForConditionalGeneration.from_pretrained(model_path, torch_dtype=torch.float16)
            self.model.to(device)
        self.prompt = prompt
        self.max_new_tokens = 100

    def get_image_caption(self, image_path):
        raw_image = Image.open(image_path).convert('RGB')
        inputs = self.processor(images=raw_image, text=self.prompt, return_tensors="pt").to(device, torch.float16)
        generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        return generated_text


if __name__ == '__main__':
    image_dir = '../data/images'
    caption_path = '../data/captions_v1.2.0_20231217_6.7b.csv'
    caption_data = open(caption_path, 'w', encoding='utf-8')

    prompt = None # 'Question: Please describe the image as detailed as possible. Answer:'

    pdb.set_trace()
    image_captioner = ImageCaptioner('../models/blip2-opt-6.7b', load_in_8bit=False, prompt=prompt)

    image_list = []

    # walk through the image directory
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith(".png"):
                image_list.append(os.path.join(root, file))

    for image_path in tqdm(image_list):
        caption_data.write(image_path + ',' + image_captioner.get_image_caption(image_path) + '\n')

    caption_data.close()
