import pdb
import warnings
import re
from utils import infer_lang_from_question
from tqdm import tqdm
from args import model_list

question_prompts = {
    "zh": {
        "单选": "这道题目只有唯一的正确选项，请只给出唯一一个大写英文字母作为答案，不包含选项后面的描述，如：A，B，E。",
        "多选": "这道题目有不小于两个可行的答案，请选出所有的正确选项，格式为连续的多个大写英文字母，不包含选项后面的描述，如：AC，BDE。",
        "填空": "每一个 '[MASK]' 对应一个最简且确定的答案，多个 '[MASK]' 的答案之间换行隔开，如：文艺复兴\n0.5\n①。",
        "解答": "这道题需要你对问题进行分析作答，请覆盖所有要点的基础上尽可能简练的表达，请以'我的分析如下：'作为开头。",
    },
    "en": {
        "single_choice": "This question has only one correct option. Please give only one uppercase letter as the answer, without the description after the option, such as: A, B, E.",
        "multiple_choices": "This question has no less than two possible answers. Please choose all the correct options, in the format of consecutive uppercase letters, without the description after the options, such as: AC, BDE.",
        "fill_in_the_blank": "Each '[MASK]' corresponds to a simple and definite answer. The answers for multiple '[MASK]'s are separated by line breaks, such as: Renaissance\n0.5\n①.",
        "discussion_questions": "This question requires you to analyze the problem in detail. Please start with 'My analysis is as follows:'.",
    }
}

# TODO： to be removed
question_noncot_prompts = question_prompts
question_cot_prompts = question_prompts

knowledge_prompt = {
    "zh": "\n我们为你提供了一些额外材料，你可以参考这些信息来回答问题，请注意它们并不一定完整，也不一定正确，它们可能有图片输入，也有可能输入图片描述，也有可能只有文字，你需要结合你之前的知识来回答。\n%s",
    "en": "\nWe provide you with some extra materials. You can refer to these materials to answer the questions. Please note that they are not necessarily complete or correct. You need to combine them with your previous knowledge to answer the questions. \n%s",
}

system_prompt = {
    "zh": "你是一名来自中国的考生，你需要运用你所学的%s知识回答这道%s题。\n%s",
    "en": "You are a student from China. You need to use your knowledge of %s to answer this %s question.\n%s",
}

image_noncot_guide_prompts = {
    "zh": {
        "image": "\n这道题目包含图片信息，请基于文字和图片信息，并按照格式给出答案。\n",
        "image_in_turn": '\n这道题目包含多张图片信息，你将通过多轮问答的方式接收到所有的图片。请注意，直到"请作答"出现之前，题目均未加载完成，你可以在每一轮对话的过程中给出你对当前信息的理解与思考，但我们只会采纳你最后一轮得出的答案作为最终结果。请基于全部的文字和图片信息，并按照格式给出答案。\n',
        "caption": "\n这道题目包含图片信息，我们使用生成的图片描述来代替图片，你可以参考这些描述来回答问题。如果你认为题目中的文字信息和描述信息不足以确定正确答案，请回答'缺少图片信息'而非随便猜测一个答案，否则请按照格式给出答案。\n",
        "no_image": "\n这道题目包含图片信息，但我们不会提供这部分信息，请基于题目中的文字信息回答问题。如果你认为题目中的文字信息不足以确定正确答案，请回答'缺少图片信息'而非随便猜测一个答案，否则请按照格式给出答案。\n",
        "pure_text_with_blank_image": "\n这道题目不包含图片信息，我们会输入一张纯黑图片，请基于文字信息，并按照格式给出答案。\n",
        "pure_text": "\n这道题目不包含图片信息，请基于文字信息，并按照格式给出答案。\n",
    },
    "en": {
        "image": "\nThis question contains image information. Please give your answer directly based on the text and image information.\n",
        "image_in_turn": '\nThis question contains multiple images. You will receive all the images through multiple rounds of dialogue. Please note that until the prompt "Please give your answer" appears, the question has not been loaded completely. You can give your understanding and thoughts on the current information during each round of dialogue, but we will only adopt the answer you obtained in the last round as the final result. Please give your answer directly based on all the text and image information.\n',
        "caption": "\nThis question contains image information. We use the generated image description to replace the image. You can refer to these descriptions to answer the questions. If you think that the text information and description information in the question are not enough to determine the correct answer, please answer 'Lack of image information' instead of guessing an answer at will. Otherwise, please give your answer directly based on the text and image information.\n",
        "no_image": "\nThis question contains image information, but we will not provide this part of the information. Please give your answer directly based on the text information in the question. If you think that the text information in the question is not enough to determine the correct answer, please answer 'Lack of image information' instead of guessing an answer at will. Otherwise, please give your answer directly based on the text and image information.\n",
        "pure_text_with_blank_image": "\nThis question does not contain image information. We will input a pure black image. Please give your answer directly based on the text information in the question.\n",
        "pure_text": "\nThis question does not contain image information. Please give your answer directly based on the text information in the question.\n",
    },
}

image_cot_guide_prompts = {
    "zh": {
        "image": "\n这道题目包含图片信息，请基于文字和图片信息，给出你对这道题的思考。\n",
        "image_in_turn": '\n这道题目包含多张图片信息，你将通过多轮问答的方式接收到所有的图片。请注意，直到"请作答"出现之前，题目均未加载完成，你可以在每一轮对话的过程中给出你对当前信息的理解与思考，但我们只会采纳你最后一轮得出的答案作为最终结果。请基于全部的文字和图片信息，给出你对这道题的思考。\n',
        "caption": "\n这道题目包含图片信息，我们使用生成的图片描述来代替图片，你可以参考这些描述来回答问题。如果你认为题目中的文字信息和描述信息不足以确定正确答案，请回答'缺少图片信息'而非随便猜测，否则请给出你对这道题的思考。\n",
        "no_image": "\n这道题目包含图片信息，但我们不会提供这部分信息，请基于题目中的文字信息回答问题。如果你认为题目中的文字信息不足以确定正确答案，请回答'缺少图片信息'而非随便猜测，否则请给出你对这道题的思考。\n",
        "pure_text_with_blank_image": "\n这道题目不包含图片信息，我们会输入一张纯黑图片，请基于文字信息，并按照格式给出答案。\n",
        "pure_text": "\n这道题目不包含图片信息，请基于文字信息，给出你对这道题的思考。\n",
    },
    "en": {  # TODO: Polish English prompts in future work
        "image": "\nThis question contains image information. Please give your answer directly based on the text and image information.\n",
        "image_in_turn": '\nThis question contains multiple images. You will receive all the images through multiple rounds of dialogue. PPlease note that until you are asked to start answering, the question has not been loaded completely. You can give your understanding and thoughts on the current information during each round of dialogue, but we will only adopt the answer you obtained in the last round as the final result. Please give your answer directly based on all the text and image information.\n',
        "caption": "\nThis question contains image information. We use the generated image description to replace the image. You can refer to these descriptions to answer the questions. If you think that the text information and description information in the question are not enough to determine the correct answer, please answer 'Lack of image information' instead of guessing an answer at will. Otherwise, please give your answer directly based on the text and image information.\n",
        "no_image": "\nThis question contains image information, but we will not provide this part of the information. Please give your answer directly based on the text information in the question. If you think that the text information in the question is not enough to determine the correct answer, please answer 'Lack of image information' instead of guessing an answer at will. Otherwise, please give your answer directly based on the text and image information.\n",
        "pure_text_with_blank_image": "\nThis question does not contain image information. We will input a pure black image. Please give your answer directly based on the text information in the question.\n",
        "pure_text": "\nThis question does not contain image information. Please give your answer directly based on the text information in the question.\n",
    },
}

ending_prompt = {
    "zh": "\n请直接给出你的答案：",
    "en": "\nPlease directly give your answer:",
}

ending_cot_prompt = {
    "zh": "\n请先在此处，逐步给出你对所给问题的思考过程、推理：",
    "en": "\nPlease show your reasoning process step by step:",
}

ending_cot_doublecheck_prompt = {
    "zh": "\n根据以上思考过程，你的最终答案是：",
    "en": "\nAccording to the reasoning you have given above, the final answer should be:",
}

CoT_identifier = "<CoT_no_image>"

fs_shot_guide_example = {
    "zh": {
        "单选": "\n回答示例：\n若$a=1,b=2$，则$a+b=$[MASK]。\nA. 0\nB. 1\nC. 2\nD. 3\n你的回答：\nD",
        "多选": "\n回答示例：\n若$a=1,b=2$，则[MASK]。\nA. $a+b=3$\nB. $a-b=1$\nC. $ab=2$\nD. $a/b=4$\n你的回答：\nAC",
        "填空": "\n回答示例：\n若$a=1,b=2$，则$a+2b=$[MASK]。\n你的回答：\n5"
    }

    # TODO: en
}

fs_end_example = {
    "zh": "\n以下为你需要回答的问题：\n"
}


def get_prompts(questions, args):
    prompted_questions = {}

    for question in tqdm(questions.values()):
        prompted_questions[question["question_id"]] = get_prompt(question, args)

    return prompted_questions


def get_prompt(question, args):
    """
    We add the prompt text here.
    """
    prompted_question = {
        "question_id": question["question_id"],
        "question_image_number": question["question_image_number"],
    }

    if args.lang is None:
        args.lang = infer_lang_from_question(question)

    question_type = question["question_type"]
    question_content = question["question_content"]
    question_image_list = question.get("question_image_list", [])
    question_knowledge = question.get("knowledge", [""])
    knowledge_content = question.get("knowledge_content")
    knowledge_image_list = question.get("knowledge_image_list", [])
    question_image_number = question["question_image_number"]
    knowledge_image_number = question.get("knowledge_image_number", 0)

    image_list = question_image_list + knowledge_image_list
    image_number = question_image_number + knowledge_image_number
    if args.in_turn and len(image_list) > 1:
        in_turn = True
    else:
        in_turn = False

    if len(question_knowledge) == 0:
        question_knowledge = [""]

    if args.cot:
        question_prompts = question_cot_prompts
        image_guide_prompts = image_cot_guide_prompts
    else:
        question_prompts = question_noncot_prompts
        image_guide_prompts = image_noncot_guide_prompts

    # TODO: fix this in future data release
    # if question_knowledge[0] is a character, we use question_knowledge
    # if question_knowledge[0] is a list(i.e. string), we use question_knowledge[0]
    if len(question_knowledge[0]) == 1 and question["question_id"].startswith("shjk"):
        prompted = system_prompt[args.lang] % (question_knowledge, question_type, question_prompts[args.lang][question_type],)
    else:
        prompted = system_prompt[args.lang] % (question_knowledge[0], question_type, question_prompts[args.lang][question_type],)

    if image_number == 0:
        if args.blank_image and args.input_type == 2:
            prompted += image_guide_prompts[args.lang]["pure_text_with_blank_image"]
            prompted_question["image_list"] = [""]
        else:
            prompted += image_guide_prompts[args.lang]["pure_text"]
    else:
        if args.input_type == 0:
            prompted += image_guide_prompts[args.lang]["no_image"]
        elif args.input_type == 1:
            prompted += image_guide_prompts[args.lang]["caption"]
        elif args.input_type == 2:
            prompted_question["image_list"] = image_list
            if in_turn:
                prompted += image_guide_prompts[args.lang]["image_in_turn"]
            else:
                prompted += image_guide_prompts[args.lang]["image"]
        elif args.input_type == 3:
            return NotImplementedError

    if args.few_shot and question_type not in ["解答", "discussion_questions"]:
        # TODO: Naive 1-shot. need deeper consideration
        prompted += fs_shot_guide_example[args.lang][question_type]
        prompted += fs_end_example[args.lang]

    if model_list[args.model]["split_sys"]:
        prompted_question["prompted_system_content"] = prompted
        prompted = ""  # TODO: Identify GPT in this way seems not so reasonable.

    prompted += question_content

    if knowledge_content is not None:
        prompted += (knowledge_prompt[args.lang] % knowledge_content)  # TODO: reduce OOM

    if args.cot and question_type not in ["解答", "discussion_questions"]:
        prompted += ending_cot_prompt[args.lang]
    else:
        prompted += ending_prompt[args.lang]

    if in_turn:
        prompted_question["prompted_content_list"] = postprocess_prompt(prompted, in_turn=True)
    else:
        prompted_question["prompted_content"] = postprocess_prompt(prompted, in_turn=False)

    if args.cot:
        if prompted_question.get("prompted_content"):
            prompted_question["prompted_content_list"] = [prompted_question.pop("prompted_content"), ending_cot_doublecheck_prompt[args.lang], ]
        else:
            prompted_question["prompted_content_list"].append(ending_cot_doublecheck_prompt[args.lang])
        if not prompted_question.get("image_list"):
            prompted_question["image_list"] = []
        prompted_question["image_list"].extend([""] * (len(prompted_question["prompted_content_list"]) - len(prompted_question["image_list"])))

    return prompted_question


def postprocess_prompt(content, in_turn=True, remove_image_token=False):
    """
    Split the prompted content into several rounds of prompts.
    """
    # find all img tokens
    match = re.findall("\[IMAGE_[0-9]+]", content)
    if in_turn:
        # Note we enter here if and only if we want to check the multi-image in_turn setting. Thus perform auto-merging here should be making sense.
        prompted_content_list = []
        # Total return len(match)+1 rounds of split prompts
        for img_sub in match:
            img_token_start = content.index(img_sub)
            if remove_image_token:
                prompted_content_list.append(content[:img_token_start].strip())
            content = content[img_token_start + len(img_sub):]
        prompted_content_list.append(content.strip())
        prompted_content_list[-2] += '\n' + prompted_content_list[-1]
        prompted_content_list.pop()
        return prompted_content_list
    else:
        for img_sub in match:
            if remove_image_token:
                content = content.replace(img_sub, "")
        return content
