"""DeepSeek-VL2 evaluator with HuggingFace Transformers"""
import pdb

import torch
from transformers import AutoModelForCausalLM
from deepseek_vl2.models import DeepseekVLV2Processor, DeepseekVLV2ForCausalLM
from deepseek_vl2.utils.io import load_pil_images


class DeepSeekVL2Evaluator:
    def __init__(self, model_dir="deepseek-ai/deepseek-vl2-tiny", max_tokens=2000, device_map="auto", use_flash_attention=True):
        self.model_dir = model_dir
        self.sample_params = {
            "max_new_tokens": max_tokens,
            "do_sample": False
        }
        
        vl_chat_processor: DeepseekVLV2Processor = DeepseekVLV2Processor.from_pretrained(self.model_dir)
        self.processor = vl_chat_processor
        self.tokenizer = vl_chat_processor.tokenizer
        
        vl_gpt: DeepseekVLV2ForCausalLM = AutoModelForCausalLM.from_pretrained(self.model_dir, trust_remote_code=True)
        self.model = vl_gpt.to(torch.bfloat16).cuda().eval()
    
    def prepare_inputs(self, question):
        image_list = question.get("image_list")
        question_content = question["prompted_content"]
        if len(image_list)==0 or image_list[0]=="":
            image_list=["../data/placeholder_black.png"]
        
        if len(image_list) == 1:
            inputs = [{
                "role": "<|User|>",
                "content": f"<image>\n<|ref|>{question_content}<|/ref|>.",
                "images": image_list,
            }, {
                "role": "<|Assistant|>",
                "content": ""
            }]
        else:
            image_content=''.join([f'This is image_{index}: <image>\n' for index in range(len(image_list))])
            inputs = [{
                "role": "<|User|>",
                "content": f"{image_content}<|ref|>{question_content}<|/ref|>.",
                "images": image_list,
            }, {
                "role": "<|Assistant|>",
                "content": ""
            }]
        return inputs
    
    def generate_response(self, input):
        if isinstance(input, dict):
            question = input
            inputs = self.prepare_inputs(question)
            
            # load images and prepare for inputs
            pil_images = load_pil_images(inputs)
            prepare_inputs = self.processor(conversations=inputs, images=pil_images, force_batchify=True, system_prompt="").to(self.model.device)
            
            # run image encoder to get the image embeddings
            inputs_embeds = self.model.prepare_inputs_embeds(**prepare_inputs)
            
            # run the model to get the response
            outputs = self.model.language.generate(inputs_embeds=inputs_embeds, attention_mask=prepare_inputs.attention_mask, pad_token_id=self.tokenizer.eos_token_id, bos_token_id=self.tokenizer.bos_token_id, eos_token_id=self.tokenizer.eos_token_id, max_new_tokens=512, do_sample=False, use_cache=True)
            
            response = self.tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=True)
            
            return response,prepare_inputs['sft_format'][0]
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
