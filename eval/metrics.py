"""
Calculate the score and generate the summary
"""

import json
import re
import pdb

import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rouge_chinese import Rouge
from tqdm import tqdm

from args import parse_args_for_score
from utils import Education_Level_Dict_zh2en, Question_Type_Dict_zh2en


def SingleAnswerChoiceEval(pred, label):
    """
    提取输出中出现的第一个英文字母作为答案
    """
    match = re.search(r'[a-zA-Z]', pred)
    if match:
        answer = match.group(0)
        score = 1 if answer == label else 0
    else:
        score = 0
    return score, 1


def MultipleAnswersChoiceEval(pred, label):
    """
    提取输出中出现的数个连续或使用','和' '间隔的英文字母作为答案，对答案去重并进行排序
    每选择一个正确选项+1分，若选择错误选项则直接得0分
    分数不进行归一化处理
    """
    match = re.search(r'[a-zA-Z ,]+', pred)
    score = 0
    if match:
        answer = match.group(0)
        answer = answer.replace(' ', '').replace(',', '').replace('、','')
        answer = ''.join(sorted(set(answer), key=answer.index))
        for choice in answer:
            if choice in label:
                score += 1
            else:
                score = 0
                break
    else:
        score = 0
    return score, len(label)


def FillInTheBlankEval(pred, label):
    """
    提取输出每一行作为一个[MASK]的答案
    我们比较答案是否严格一致，部分选项有多重正确答案，使用“或”进行分割
    """
    score = 0
    pred = pred.split('\n')
    label = label.split('\n')
    for i in range(min(len(label), len(pred))):
        if pred[i] == label[i]:
            score += 1
        else:
            alternatives = label[i].split('或')
            if len(alternatives) > 1:
                if pred[i] in alternatives:
                    score += 1
                    continue

    return score, len(label)


def OpenendQuestionEval(pred, label):
    """
    使用ROUGE来计算答案与标准答案的相似度
    Please be aware that Evaluation of Discussion Questions is not accurate, and may not reflect the real quality of the answer.
    """
    rouge = Rouge()
    pred_ = ' '.join(jieba.cut(pred))
    label_ = ' '.join(jieba.cut(label))
    if label_ == '':
        return 0, 0
    rouge_score = rouge.get_scores(pred_, label_, avg=True)
    score = rouge_score['rouge-l']['f']
    return score, 1


EvaluateFuncDict = {
    "单选": SingleAnswerChoiceEval,
    "多选": MultipleAnswersChoiceEval,
    "填空": FillInTheBlankEval,
    "解答": OpenendQuestionEval
}


def evaluate_every_problem(args):
    """
    计算每道题的绝对分数
    pred:
    {question_id,prediction,}
    score:
    {question_id,score,total_score}
    """
    with open(args.prediction_file, 'r', encoding="utf-8") as f:
        pred_data = json.load(f)
    with open(args.label_file, 'r', encoding="utf-8") as f:
        label_data = json.load(f)

    score_data = {}

    # sort by question_id, be aware of the numbers in the question_id course_number1_number2
    pred_data = dict(sorted(pred_data.items(), key=lambda x: (x[0].split('_')[0])))

    for item in pred_data.values():
        problem_id, sub_id = item['question_id'].rsplit('_', 1)
        label = label_data[problem_id]["problem_answer_list"][int(sub_id)].strip()
        type = label_data[problem_id]["problem_type_list"][int(sub_id)]

        if type in EvaluateFuncDict:
            score, total_score = EvaluateFuncDict[type](item['prediction'], label)
        else:
            score, total_score = 0, 0

        score_data[item['question_id']] = {
            "question_id": item['question_id'],
            "score": score,
            "total_score": total_score
        }

        pred_data[item['question_id']]["answer"] = label
        pred_data[item['question_id']]["score"] = score
        pred_data[item['question_id']]["total_score"] = total_score
        pred_data[item['question_id']]["type"] = type
        pred_data[item['question_id']]["education"] = label_data[problem_id]["education"]
        pred_data[item['question_id']]["subject"] = label_data[problem_id]["subject"][0]

    with open(args.prediction_file.replace('prediction.json', 'score.json'), 'w', encoding="utf-8") as f:
        json.dump(score_data, f, indent=4, ensure_ascii=False)

    with open(args.detail_file, 'w', encoding="utf-8") as f:
        json.dump(pred_data, f, indent=4, ensure_ascii=False)


def calculate_score(args):
    with open(args.score_file, 'r', encoding="utf-8") as f:
        target_score = json.load(f)

    absolute_score = 0
    total_absolute_score = 0

    for item in target_score.values():
        absolute_score += item['score']
        total_absolute_score += item['total_score']

    print(absolute_score,total_absolute_score,absolute_score / total_absolute_score * 100)

    # TODO: add a relative method to calculate scores, this method should be applied to single calculation as absolute score


def init_dict(detail_data, education, subject):
    type_list = [i for i in Question_Type_Dict_zh2en.values() if i != "Other"]
    image_list = ["NI", "SI", "MI"]
    if education not in detail_data:
        detail_data[education] = {}
    if subject not in detail_data[education]:
        detail_data[education][subject] = {}
        for type in type_list:
            detail_data[education][subject][type] = {}
            for image in image_list:
                detail_data[education][subject][type][image] = {
                    "count": 0,
                    "correct": 0,
                    "total": 0,
                    "score": 0
                }

    return detail_data


def detail_score(args):
    with open(args.detail_file, 'r', encoding="utf-8") as f:
        score_data = json.load(f)

    with open(args.label_file, 'r', encoding="utf-8") as f:
        label_data = json.load(f)

    detail_file = open(args.prediction_file.replace('prediction.json', 'statistics.csv'), 'w', encoding="utf-8")

    detail_file.write('education,subject,type,image,qs_count,qs_correct,qs_total,qs_score\n')
    # store the score in a 5-dimension dict
    detail_data = {}

    for item in tqdm(score_data.values()):
        question_id = item['question_id']
        education = Education_Level_Dict_zh2en[item["education"]]
        subject = item["subject"]
        if subject == "驾考":
            education = "Driving"
        elif subject == "行测":
            education = "AAT"
        type = Question_Type_Dict_zh2en[item["type"]]
        if type == "其他":
            continue
        detail_data = init_dict(detail_data, education, subject)

        image_num = item["question_image_number"]  # get_image_number(question_id,label_data)
        image = "NI" if image_num == 0 else "SI" if image_num == 1 else "MI"

        # update the detail_data
        detail_data[education][subject][type][image]["count"] += 1
        detail_data[education][subject][type][image]["correct"] += 1 if item['score'] == item['total_score'] else 0
        detail_data[education][subject][type][image]["total"] += item['total_score']
        detail_data[education][subject][type][image]["score"] += item['score']

    # write the detail_data into the detail_file
    for education in detail_data:
        for subject in detail_data[education]:
            for type in detail_data[education][subject]:
                for image in detail_data[education][subject][type]:
                    detail_file.write(
                        f'{education},{subject},{type},{image},{detail_data[education][subject][type][image]["count"]},{detail_data[education][subject][type][image]["correct"]},{detail_data[education][subject][type][image]["total"]},{detail_data[education][subject][type][image]["score"]}\n')

    detail_file.close()


def generate_summary(args):
    # prepare the data
    # summary_data[education][image][type]
    # read csv file
    detail_csv = pd.read_csv(args.prediction_file.replace('prediction.json', 'statistics.csv'), encoding="utf-8")
    summary_file = open(args.prediction_file.replace('prediction.json', 'summary.md'), 'w')

    summary_data = {}

    for education in detail_csv['education'].unique():
        summary_data[education] = {}
        for image in detail_csv['image'].unique():
            summary_data[education][image] = {}
            for type in detail_csv['type'].unique():
                summary_data[education][image][type] = {
                    "count": 0,
                    "correct": 0,
                    "total": 0,
                    "score": 0
                }

    for index, row in detail_csv.iterrows():
        education = row['education']
        image = row['image']
        type = row['type']
        summary_data[education][image][type]["count"] += row['qs_count']
        summary_data[education][image][type]["correct"] += row['qs_correct']
        summary_data[education][image][type]["total"] += row['qs_total']
        summary_data[education][image][type]["score"] += row['qs_score']

    # print(summary_data)
    print("=" * 10 + " Calculating by Education Level " + "=" * 10)

    # now we only spilt by education
    summary_data_by_education = {}
    for education in summary_data:
        summary_data_by_education[education] = {
            "count": 0,
            "correct": 0,
            "total": 0,
            "score": 0
        }
        for image in summary_data[education]:
            for type in summary_data[education][image]:
                summary_data_by_education[education]["count"] += summary_data[education][image][type]["count"]
                summary_data_by_education[education]["correct"] += summary_data[education][image][type]["correct"]
                summary_data_by_education[education]["total"] += summary_data[education][image][type]["total"]
                summary_data_by_education[education]["score"] += summary_data[education][image][type]["score"]

    print(summary_data_by_education)

    # print in the markdown format
    summary_file.write('\n\n| Education | Correct  | Score | Ratio |\n')
    summary_file.write('| ---- | ---------- | --------- | ------ |\n')
    for education in summary_data_by_education:
        if summary_data_by_education[education]["total"] > 0:
            summary_file.write(
                f'| {education} | {summary_data_by_education[education]["correct"]}/{summary_data_by_education[education]["count"]} | {summary_data_by_education[education]["score"]}/{summary_data_by_education[education]["total"]} | {summary_data_by_education[education]["score"] / summary_data_by_education[education]["total"] * 100:.1f} |\n')

    # draw bar chart, each bar has a height of the total score in green, and a part of the bar is in red with score, and a line to indicate the correct rate in blue
    plt.figure(figsize=(10, 6))
    # bars are in log scale on the left
    ax1 = plt.gca()
    ax1.bar(summary_data_by_education.keys(), [summary_data_by_education[education]["total"] for education in summary_data_by_education], color='green')
    ax1.bar(summary_data_by_education.keys(), [summary_data_by_education[education]["score"] for education in summary_data_by_education], color='red')
    ax1.set_yscale('log')
    ax1.set_ylim(50, 20000)

    # the line is in linear scale on the right
    ax2 = plt.twinx()
    ax2.plot(summary_data_by_education.keys(), [summary_data_by_education[education]["score"] / (summary_data_by_education[education]["total"] * 100 + 0.001) for education in summary_data_by_education], color='blue')
    ax2.set_title(f'Score Summary by Education Level\n{args.prediction_file.split("/")[-2].rsplit("_", 2)[0]}')
    plt.tight_layout()
    plt.savefig(args.prediction_file.replace('prediction.json', 'summary_education.png'))
    summary_file.write('\n\n![summary_education](summary_education.png)\n')

    print("=" * 10 + " Calculating by Image Number " + "=" * 10)

    # now we only spilt by image
    summary_data_by_image = {}
    for education in summary_data:
        for image in summary_data[education]:
            if image not in summary_data_by_image:
                summary_data_by_image[image] = {
                    "count": 0,
                    "correct": 0,
                    "total": 0,
                    "score": 0
                }
            for type in summary_data[education][image]:
                if type == 'Other':
                    pdb.set_trace()
                summary_data_by_image[image]["count"] += summary_data[education][image][type]["count"]
                summary_data_by_image[image]["correct"] += summary_data[education][image][type]["correct"]
                summary_data_by_image[image]["total"] += summary_data[education][image][type]["total"]
                summary_data_by_image[image]["score"] += summary_data[education][image][type]["score"]

    print(summary_data_by_image)

    # print in the markdown format
    summary_file.write('\n\n| Image  | Correct  | Score | Ratio |\n')
    summary_file.write('| ---- | ---------- | --------- | ------ |\n')
    for image in summary_data_by_image:
        if summary_data_by_image[image]["total"] > 0:
            summary_file.write(
                f'| {image} | {summary_data_by_image[image]["correct"]}/{summary_data_by_image[image]["count"]} | {summary_data_by_image[image]["score"]}/{summary_data_by_image[image]["total"]} | {summary_data_by_image[image]["score"] / summary_data_by_image[image]["total"] * 100:.1f} |\n')

    # draw bar chart, each bar has a height of the total score in green, and a part of the bar is in red with score, and a line to indicate the correct rate in blue
    plt.figure(figsize=(10, 6))
    # bars are in log scale on the left
    ax1 = plt.gca()
    ax1.bar(summary_data_by_image.keys(), [summary_data_by_image[image]["total"] for image in summary_data_by_image], color='green')
    ax1.bar(summary_data_by_image.keys(), [summary_data_by_image[image]["score"] for image in summary_data_by_image], color='red')
    ax1.set_yscale('log')
    ax1.set_ylim(5, 20000)
    # the line is in linear scale on the right
    ax2 = plt.twinx()
    ax2.plot(summary_data_by_image.keys(), [summary_data_by_image[image]["score"] / (summary_data_by_image[image]["total"] * 100 + 0.001) for image in summary_data_by_image], color='blue')
    ax2.set_title(f'Score Summary by Image Number\n{args.prediction_file.split("/")[-2].rsplit("_", 2)[0]}')
    plt.tight_layout()
    plt.savefig(args.prediction_file.replace('prediction.json', 'summary_image.png'))
    summary_file.write('\n\n![summary_image](summary_image.png)\n')

    print("=" * 10 + " Calculating by Question Type " + "=" * 10)

    # now we only spilt by type
    summary_data_by_type = {}
    for education in summary_data:
        for image in summary_data[education]:
            for type in summary_data[education][image]:
                if type != 'Other' and type not in summary_data_by_type:
                    summary_data_by_type[type] = {
                        "count": 0,
                        "correct": 0,
                        "total": 0,
                        "score": 0
                    }
                summary_data_by_type[type]["count"] += summary_data[education][image][type]["count"]
                summary_data_by_type[type]["correct"] += summary_data[education][image][type]["correct"]
                summary_data_by_type[type]["total"] += summary_data[education][image][type]["total"]
                summary_data_by_type[type]["score"] += summary_data[education][image][type]["score"]

    print(summary_data_by_type)

    # print in the markdown format
    summary_file.write('\n\n| Type | Correct  | Score | Ratio |\n')
    summary_file.write('| ---- | ---------- | --------- | ------ |\n')
    for type in summary_data_by_type:
        if summary_data_by_type[type]["total"] > 0:
            summary_file.write(
                f'| {type} | {summary_data_by_type[type]["correct"]}/{summary_data_by_type[type]["count"]} | {summary_data_by_type[type]["score"]}/{summary_data_by_type[type]["total"]} | {summary_data_by_type[type]["score"] / summary_data_by_type[type]["total"] * 100:.1f} |\n')

    # draw bar chart, each bar has a height of the total score in green, and a part of the bar is in red with score, and a line to indicate the correct rate in blue
    plt.figure(figsize=(10, 6))
    # bars are in log scale on the left
    ax1 = plt.gca()
    ax1.bar(summary_data_by_type.keys(), [summary_data_by_type[type]["total"] for type in summary_data_by_type], color='green')
    ax1.bar(summary_data_by_type.keys(), [summary_data_by_type[type]["score"] for type in summary_data_by_type], color='red')
    ax1.set_yscale('log')
    ax1.set_ylim(50, 20000)
    # the line is in linear scale on the right
    ax2 = plt.twinx()
    ax2.plot(summary_data_by_type.keys(), [summary_data_by_type[type]["score"] / (summary_data_by_type[type]["total"] * 100 + 0.001) for type in summary_data_by_type], color='blue')
    ax2.set_title(f'Score Summary by Question Type\n{args.prediction_file.split("/")[-2].rsplit("_", 2)[0]}')
    plt.tight_layout()
    plt.savefig(args.prediction_file.replace('prediction.json', 'summary_type.png'))
    summary_file.write('\n\n![summary_type](summary_type.png)\n')

    with open(args.detail_file, 'r', encoding="utf-8") as f:
        detail_data = json.load(f)
    # draw heatmap there are 100 blocks in each column, there are question_number/100 row in total, each block is a question, the depth of the color indicates the score of the question, if the question is correct, the color is deep, otherwise it is light.
    plt.figure(figsize=(10, 6))

    heatmap_data = np.zeros((100, np.ceil(len(detail_data) / 100).astype(int)))
    for i, question_id in enumerate(detail_data):
        heatmap_data[i % 100, i // 100] = detail_data[question_id]["score"] / (detail_data[question_id]["total_score"]+0.001)

    plt.imshow(heatmap_data, cmap='RdYlGn', interpolation='nearest', vmin=-0.25, vmax=1.25)
    ax = plt.gca()
    ax.set_yticks(np.arange(0, 120, 20))
    ax.set_title(f'Heatmap of the Score\n{args.prediction_file.split("/")[-2].rsplit("_", 2)[0]}')

    plt.tight_layout()
    plt.savefig(args.prediction_file.replace('prediction.json', 'heatmap.png'))
    summary_file.write('\n\n![heatmap](heatmap.png)\n')


def main(args):
    if args.prediction_file and args.label_file:
        # calculate the absolute score of each problem
        args.score_file = args.prediction_file.replace('prediction.json', 'score.json')
        args.detail_file = args.prediction_file.replace('prediction.json', 'detail.json')
        print(f"\nCalculating the absolute score of {args.prediction_file.split('/')[-2]}")
        evaluate_every_problem(args)

    calculate_score(args)

    if args.detail:
        detail_score(args)
        generate_summary(args)

if __name__ == "__main__":
    args = parse_args_for_score()
    main(args)
