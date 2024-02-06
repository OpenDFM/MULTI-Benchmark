"""
Generate image ocr content using EasyOCR.
"""

import torch
from PIL import Image
import os
from tqdm import tqdm
import easyocr
import numpy as np

torch.backends.cudnn.enabled = False


class ImageOCR:
    def __init__(self):
        self.reader = easyocr.Reader(['ch_sim', 'en'])

    def get_image_ocr(self, image_path):
        image = Image.open(image_path)
        textlist = self.reader.readtext(np.array(image))
        text = "、".join(map(lambda x: x[1], textlist))
        return text


if __name__ == '__main__':
    image_dir = '../data/images'
    ocr_path = '../data/ocr_v1.2.0_20231217.csv'
    ocr_data = open(ocr_path, 'w', encoding='utf-8')

    image_ocr_reader = ImageOCR()

    image_list = []

    # walk through the image directory
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith(".png"):
                image_list.append(os.path.join(root, file))

    for image_path in tqdm(image_list):
        ocr_data.write(image_path + ',' + image_ocr_reader.get_image_caption(image_path) + '\n')

    ocr_data.close()
