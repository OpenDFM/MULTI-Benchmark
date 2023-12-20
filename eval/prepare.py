import os
import json
import re
import csv
import pdb

from tqdm import tqdm

from args import parse_args_for_eval
import random


def select_questions(args):
    """
    return a list of question ids
    """
    with open(args.problem_file, "r", encoding="utf-8") as f:
        problems = json.load(f)

    question_list = []

    if args.subset:
        for problem_id in problems:
            for i in range(len(problems[problem_id]["problem_type_list"])):
                question_list.append(problem_id + "_" + str(i))

        # subset is a txt file containing the ids of the problems to be evaluated, one id per line
        with open(args.subset, "r", encoding="utf-8") as f:
            subset = json.load(f)
        # get intersection of subset and question_list
        question_list = list(set(question_list) & set(subset))

    else:
        all_type_list = ["单选", "多选", "填空", "解答", "其他"]
        type_list = []
        args.questions_type = [int(i) for i in args.questions_type.split(",")]
        for i in args.questions_type:
            type_list.append(all_type_list[i])

        for problem_id in problems:
            # select problems with the specified subject
            if not args.subject or problem_id.split("_")[0] == args.subject:
                for i in range(len(problems[problem_id]["problem_type_list"])):  #
                    # select problems with the specified type
                    if problems[problem_id]["problem_type_list"][i] in type_list:
                        question_list.append(problem_id + "_" + str(i))

    return question_list

def shuffle_questions(args,questions):
    args.image_type = [int(i) for i in args.image_type.split(",")]
    question_list = list(questions.keys())
    questions_tmp = {}
    question_list_tmp = []

    for question_id in question_list:
        image_number = questions[question_id]["question_image_number"]
        if min(image_number,2) in args.image_type:
            question_list_tmp.append(question_id)

    if args.random:
        random.shuffle(question_list_tmp)

    if args.eval_num > 0:
        question_list_tmp = question_list_tmp[: args.eval_num]

    for question_id in question_list_tmp:
        questions_tmp[question_id] = questions[question_id]
    return questions_tmp


def modify_image_content(content, image_list, caption_data=None, caption_in_content=False):
    """
    Modify the image related parts in the content
    """

    new_content, new_image_list = content, []

    match = re.findall(r"<img_[0-9]+>", content)
    image_number = len(match)

    if match:
        new_image_index = [int(i.replace("<img_", "").replace(">", "")) - 1 for i in match]
        for i in new_image_index:
            new_image_list.append(image_list[i])

        if caption_data:
            caption_list = []
            for image in new_image_list:
                try:
                    caption_list.append(caption_data[image])
                except:
                    caption_list.append("")

        for i in range(len(match)):
            if caption_in_content and caption_list:
                new_content = new_content.replace(match[i], f"<img_{i + 1}:{caption_list[i]}>")
            else:
                new_content = new_content.replace(match[i], f"<img_{i + 1}>")

        if caption_data:
            if not caption_in_content:
                for i in range(len(caption_list)):
                    new_content += f"<img_{i + 1}>: {caption_list[i]}\n"

    # assert len(new_image_list) == image_number, "The number of images in the content does not match the number of images in the image list."
    return new_content, new_image_list, image_number


def prepare_question(question_id, input_data, knowledge_data, caption_data, args):
    """
    We do not add any prompt text here.
    """

    question_info = {
        "question_id": question_id
    }
    # if question_id =="gzsw_26_0":
    #     pdb.set_trace()
    problem_id, sub_id = question_id.rsplit("_", 1)
    question_info["question_content"] = (input_data[problem_id]["problem_content"] + "\n" + input_data[problem_id]["problem_content_list"][int(sub_id)])
    question_info["question_type"] = input_data[problem_id]["problem_type_list"][int(sub_id)]

    question_info["knowledge"] = input_data[problem_id]["knowledge"]
    try:
        knowledge_info = knowledge_data[question_info["knowledge"][0]]
        question_info["knowledge_content"] = knowledge_info["knowledge_content"]
    except:
        knowledge_info = None

    if args.input_type == 0:
        question_info["question_content"], _, question_info["question_image_number"] = modify_image_content(question_info["question_content"], input_data[problem_id]["img_paths"])
    elif args.input_type == 1:
        question_info["question_content"], _, question_info["question_image_number"] = modify_image_content(question_info["question_content"], input_data[problem_id]["img_paths"], caption_data=caption_data, caption_in_content=args.cap_in_cnt)
    elif args.input_type == 2:
        question_info["question_content"], question_info["question_image_list"], question_info["question_image_number"] = modify_image_content(question_info["question_content"], input_data[problem_id]["img_paths"])
    elif args.input_type == 3:
        return NotImplementedError

    if knowledge_info:
        if args.input_type == 0:
            question_info["knowledge_content"], _, question_info["knowledge_image_number"] = modify_image_content(question_info["knowledge_content"], knowledge_info["knowledge_images"])
        elif args.input_type == 1:
            question_info["knowledge_content"], _, question_info["knowledge_image_number"] = modify_image_content(question_info["knowledge_content"], knowledge_info["knowledge_images"], caption_data=caption_data, caption_in_content=args.cap_in_cnt)
        elif args.input_type == 2:
            question_info["knowledge_content"], question_info["knowledge_image_list"], question_info["knowledge_image_number"] = modify_image_content(question_info["knowledge_content"], knowledge_info["knowledge_images"])
        elif args.input_type == 3:
            return NotImplementedError

    return question_info


def prepare_questions(args):
    """
    return a dict of questions with question_id from question_list as key
    IMPORTANT: question_id IS problem_id + "_" + sub_id
    """
    with open(args.problem_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    if isinstance(input_data, list):
        input_data = {problem['problem_id']: problem for problem in input_data}

    if args.knowledge_file:
        with open(args.knowledge_file, "r", encoding="utf-8") as f:
            knowledge_data = json.load(f)
    else:
        knowledge_data = {}

    if args.input_type == 1:
        if args.caption_file:
            # csv file
            # image_path, caption
            with open(args.caption_file, "r", encoding="utf-8") as f:
                caption_data = {}
                for line in f:
                    caption_data[line.split(",", 1)[0].strip()] = line.split(",", 1)[1].strip()
        else:
            raise FileNotFoundError("Caption file not specified. Please specify the caption file.")
    else:
        caption_data = {}

    question_list = select_questions(args)
    questions = {}

    for question_id in tqdm(question_list):
        questions[question_id] = prepare_question(question_id, input_data, knowledge_data, caption_data, args)

    questions = shuffle_questions(args, questions)

    return questions
