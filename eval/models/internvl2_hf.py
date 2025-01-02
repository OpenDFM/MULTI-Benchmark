"""InternVL2 Evaluator with HuggingFace Transformers"""
import math
import re
import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoModel, AutoTokenizer

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def build_transform(input_size):
    MEAN, STD = IMAGENET_MEAN, IMAGENET_STD
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=MEAN, std=STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio

def dynamic_preprocess(image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
        i * j <= max_num and i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images

def load_image(image_file, input_size=448, max_num=12):
    image = Image.open(image_file).convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image, image_size=input_size, use_thumbnail=True, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values

def split_model(model_name):
    device_map = {}
    world_size = torch.cuda.device_count()
    num_layers = {
        'InternVL2-1B': 24, 'InternVL2-2B': 24, 'InternVL2-4B': 32, 'InternVL2-8B': 32,
        'InternVL2-26B': 48, 'InternVL2-40B': 60, 'InternVL2-Llama3-76B': 80}[model_name]
    # Since the first GPU will be used for ViT, treat it as half a GPU.
    num_layers_per_gpu = math.ceil(num_layers / (world_size - 0.5))
    num_layers_per_gpu = [num_layers_per_gpu] * world_size
    num_layers_per_gpu[0] = math.ceil(num_layers_per_gpu[0] * 0.5)
    layer_cnt = 0
    for i, num_layer in enumerate(num_layers_per_gpu):
        for j in range(num_layer):
            device_map[f'language_model.model.layers.{layer_cnt}'] = i
            layer_cnt += 1
    device_map['vision_model'] = 0
    device_map['mlp1'] = 0
    device_map['language_model.model.tok_embeddings'] = 0
    device_map['language_model.model.embed_tokens'] = 0
    device_map['language_model.output'] = 0
    device_map['language_model.model.norm'] = 0
    device_map['language_model.lm_head'] = 0
    device_map[f'language_model.model.layers.{num_layers - 1}'] = 0
    device_map['language_model.model.rotary_emb'] = 0

    return device_map

class InternVLEvaluator():
    def __init__(self, model_dir="OpenGVLab/InternVL2-8B", device_map="auto"):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": 2000,
            "do_sample": True,
            "temperature": 0.2,
        }
        print(f"Using GPU: {torch.cuda.device_count()}")
        # if torch.cuda.device_count()>1:
        #     device_map=split_model(model_dir.split("/")[-1])
        
        self.tokenizer =AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True, use_fast=False)
        self.tokenizer.model_max_length = 8192
        USE_8_BIT =False
        USE_4_BIT =False
        if "AWQ" in model_dir:
            self.model = AutoModel.from_pretrained(self.model_dir, torch_dtype=torch.float16, use_flash_attn=True, trust_remote_code=True, device_map=device_map).eval()
        elif USE_8_BIT:
            self.model = AutoModel.from_pretrained(self.model_dir, torch_dtype=torch.bfloat16, load_in_8bit=True,use_flash_attn=True, trust_remote_code=True, device_map=device_map).eval()
        elif USE_4_BIT:
            self.model = AutoModel.from_pretrained(self.model_dir, torch_dtype=torch.bfloat16, load_in_4bit=True,use_flash_attn=True, trust_remote_code=True, device_map=device_map).eval()
        else:
            self.model = AutoModel.from_pretrained(self.model_dir, torch_dtype=torch.bfloat16, use_flash_attn=True, trust_remote_code=True, device_map=device_map).eval()
            
     

    def prepare_inputs(self, question):
        image_list = question.get("image_list")
        content=question["prompted_content"]

        if image_list:
            match = re.findall("<img_[0-9]+>", content)
            content_prefix = ""
            if len(match) > 0:
                if len(image_list) == 1:
                    content = content.replace(match[0], "<image>\n")
                else:
                    for i, img_sub in enumerate(match):
                        content = content.replace(img_sub, f"Image-{i+1}: <image>\n")
            elif len(image_list) > 0:
                if len(image_list) == 1:
                    content_prefix += f"<image>\n" # align with our previous setting
                else:
                    for i, image_path in enumerate(image_list):
                        content_prefix += f"Image-{i+1}: <image>\n"
            content = content_prefix + content

            """
            # multi-image multi-round conversation, separate images (多图多轮对话，独立图像)
            pixel_values1 = load_image('./examples/image1.jpg', max_num=12).to(torch.bfloat16).cuda()
            pixel_values2 = load_image('./examples/image2.jpg', max_num=12).to(torch.bfloat16).cuda()
            pixel_values = torch.cat((pixel_values1, pixel_values2), dim=0)
            num_patches_list = [pixel_values1.size(0), pixel_values2.size(0)]
            """

            # load pixel values
            pixel_values_list = []
            num_patches_list=[]

            for image_path in image_list:
                pixel_value=load_image(image_path, max_num=12).to(torch.bfloat16).cuda()
                num_patches_list.append(pixel_value.size(0))
                pixel_values_list.append(pixel_value)

            pixel_values = torch.cat(pixel_values_list, dim=0)
        else:
            pixel_values=None
            num_patches_list=[]

        return content,pixel_values,num_patches_list

    def generate_response(self, input):
        if isinstance(input, dict):
            question = input

            message,pixel_values,num_patches_list = self.prepare_inputs(question)

            response, history = self.model.chat(self.tokenizer, pixel_values, message, self.sample_params,num_patches_list=num_patches_list,history=None, return_history=True)

            return response, message

        elif isinstance(input, tuple):
            raise ValueError(f"input type not supported: {type(input)}")
        else:
            raise ValueError(f"input type not supported: {type(input)}")

    def generate_answer(self, question):
        if question.get("prompted_content"):
            response, message = self.generate_response(question)
            question["input_message"] = message
            question.pop("prompted_content")
        elif question.get("prompted_content_list"):
            raise ValueError(f"Question not supported: {question}")
        else:
            raise ValueError(f"Question not supported: {question}")
        question["prediction"] = response
        return question
