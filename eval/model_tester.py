"""
Note: To avoid the confusion of Python dynamic modules, use this file to enable module test.
"""

from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--model", "-m", type=str, default="viscpm", help="The module name to be tested", )
    parser.add_argument("--model_dir", "-p", type=str, default=None, help="specified model checkpoint path. If not set, use the one defined in modules.", )
    parser.add_argument("--lang", "-l", default="zh", choices=["en", "zh"], help="language")
    parser.add_argument("--in_turn", action="store_true", help="Whether to use in-turn input for multi-image questions. If not, the model will receive all the images at once.", )
    parser.add_argument("--input_type", type=int, choices=range(0, 4), default=0, help="Specify the input type. 0 - only_text, 1 - text_with_captions, 2 - text_and_images, 3 - only_images. By leaving it empty, it means only_text.", )
    parser.add_argument("--blank_image", action="store_true", help="If the input type is 2, whether to use blank image as the placeholder for the image.", )
    parser.add_argument("--model_version", "-v", type=str, default=None, help="Specify the model type. You need to fill in this if you want to test specific model version.", )
    parser.add_argument("--use_modelscope", action="store_true", help="whether to use modelscope")
    parser.add_argument("--few_shot", "-k", type=int, default=0, help="Specify the number of few shot samples. By leaving it empty, it means zero-shot k=0.", )
    parser.add_argument("--cot", action="store_true", help="Whether to use chain-of-thought.")
    parser.add_argument("--cuda_device", "-c", type=str, default="cpu", help='Specify the cuda device. By leaving it empty, it means using cpu. You can specify multiple cuda devices by separating them with commas, i.e. "0,1,2,3".', )
    return parser.parse_args()


from prompts import get_prompts

#### Fabricate some examples for testing. Note, these test cases covers a lot of aspects and may have some value for validating the performance.

testcases_for_english = [{
    "question_type": "single_choice",
    "question_content": r"If $x=3$, then [MASK] \nA. $x-3=-1$ \nB. $x+2=5$ \nC. $x^2=10$ \nD. $\sqrt x=2$",
    "correct_answer": "B"
}, {
    "question_type": "single_choice",
    "question_content": "$\\lim\\limits_{x\\rightarrow0}\\frac{(1+x)^{\\frac 1x}-e}x=$[MASK] \nA. $1$ \nB. $-1$ \nC. $-\\frac 12$ \nD. $-\\frac e2$",
    "correct_answer": "D"
}, ]  # Pure Text only

testcases_for_chinese = [{
    "question_type": "单选",
    "question_content": "在$\\triangle ABC$中，$AB=AC=BC=2$, $AM$是底边$BC$上的高，则$BM=$ [MASK].\nA. $1$ \nB. $\\sqrt 3$ \nC. $\\frac 12$ \nD. $\\frac {\\sqrt 3}2$",
    "correct_answer": "A"
}, {
    "question_type": "单选",
    "question_content": "下列说法中,正确的是[MASK] \nA. 可能性很大的事情是必然发生的 \nB. 可能性很小的事情是不可能发生的 \nC. 可能性很小的事件在一次实验中有可能发生 \nD. 掷一枚普通的正方体骰子,结果恰好点数“5”朝上是不可能发生的",
    "correct_answer": "C"
}, {
    "question_type": "单选",
    "question_content": "$\\lim\\limits_{x\\rightarrow0}\\frac{(1+x)^{\\frac 1x}-e}x=$[MASK] \nA. $1$ \nB. $-1$ \nC. $-\\frac 12$ \nD. $-\\frac e2$",
    "correct_answer": "D"
}, {
    "question_type": "单选",
    "question_content": "如图，$AB=AC=BC=2$, 则$BM=$ [MASK] <img_1>\nA. $1$ \nB. $\\sqrt 3$ \nC. $\\frac 12$ \nD. $\\frac {\\sqrt 3}2$",
    "question_image_list": ["data_sample/sample_pic.png"],
    "correct_answer": "A"
}, {
    "question_type": "单选",
    "question_content": "<img_1>\n如图，$AB=AC=BC=2$, 则$BM=$ [MASK].<img_2>\nA. $1$ \nB. $\\sqrt 3$ \nC. $\\frac 12$ \nD. $\\frac {\\sqrt 3}2$",
    "question_image_list": ["data_sample/sample_pic.png", "data_sample/sample_pic.png", ],
    "correct_answer": "A"
}, {
    "question_type": "单选",
    "question_content": "关于以下两张图片，描述正确的是 [MASK].<img_1><img_2>\nA. 这两张图片描述不同的几何形 \nB. 第一张图中，点$C$是线段BM的$中点$ \nC. 第二张图中，点$A,B,M,C$构成平行四边形 \nD. 两张图片完全相同",
    "question_image_list": ["data_sample/sample_pic.png", "data_sample/sample_pic.png", ],
    "correct_answer": "D"
}, {
    "question_type": "填空",
    "question_content": "如图，$AB=AC=BC=2$, 则$BM=$ [MASK] <img_1>\n",
    "question_image_list": ["data_sample/sample_pic.png"],
    "correct_answer": "1"
}, {
    "question_type": "多选",
    "question_content": "下图中列出了若干个国家或地区的国旗或区旗，包含的国家或地区有[MASK]。<img_1>\nA. 澳门\nB. 美国\nC. 土耳其\nD. 新加坡\nE. 新西兰",
    "knowledge": ["地理"],
    "question_image_list": ["data_sample/302_1.png"],
    "correct_answer": "AC"
}, {
    "question_type": "单选",
    "question_content": "下图中列出了若干个国家或地区的国旗或区旗，包含的国家或地区有[MASK]。<img_1>\nA. 英国\nB. 美国\nC. 土耳其\nD. 新加坡",
    "knowledge": ["地理"],
    "question_image_list": ["data_sample/302_1.png"],
    "correct_answer": "C"
}, {
    "question_type": "解答",
    "question_content": "<img_1>\n请描述所给图片中包含的形状、特征，给出可能与之有关的话题。[MASK]",
    "knowledge": ["通识"],
    "question_image_list": ["data_sample/302_1.png"],
}, {
    "question_type": "解答",
    "question_content": "请描述所给图片中包含的形状、特征，给出可能与之有关的话题。<img_1>[MASK]",
    "knowledge": ["通识"],
    "question_image_list": ["data_sample/118_1.png"],
}, {
    "question_type": "解答",
    "question_content": "请描述所给图片中包含的形状、特征，给出可能与之有关的话题。<img_1>[MASK]",
    "knowledge": ["通识"],
    "question_image_list": ["data_sample/400_1.png"],
}, {
    "question_type": "解答",
    "question_content": "请描述所有给出图片中包含的形状、特征，给出可能与之有关的话题。<img_1><img_2><img_3>[MASK]",
    "knowledge": ["通识"],
    "question_image_list": ["data_sample/302_1.png", "data_sample/118_1.png", "data_sample/sample_pic.png", ],
}, ]

testcases_for_chinese_puretext = testcases_for_chinese[:3]
testcases_for_chinese_pic_descrip = testcases_for_chinese[-5:-1]

from eval import get_evaluator

if __name__ == "__main__":
    import json

    test_args = parse_args()

    # 1. evaluator
    evaluator = get_evaluator(test_args)
    # 2. test_case
    if test_args.lang == "en":
        testcases = testcases_for_english
        kn_for_test = "Mathematics"
    else:
        kn_for_test = "数学"
        # if test_args.input_type == 0:
        #     testcases = testcases_for_chinese
        # else:
    testcases = testcases_for_chinese
    # testcases = testcases_for_chinese_pic_descrip[-1:]
    # testcases = testcases_for_chinese[-1:]

    testcases = dict(zip(range(len(testcases)), testcases))
    for i in testcases:
        testcases[i].update({
            "question_id": i
        })
        if not testcases[i].get("knowledge"):
            testcases[i].update({
                "knowledge": [kn_for_test]
            })
        testcases[i]["question_image_number"] = (len(testcases[i]["question_image_list"]) if testcases[i].get("question_image_list") else 0)
    # 3. evaluate
    # As the workflow changed, we now encourage prompted questions outside of evaluators.
    # for model specific prompt, _prepare_inputs can still be used, but may have less function than before.

    prompted_questions = get_prompts(testcases, test_args)
    final_answers = []
    multiple_round_splitter = "\n" + "-" * 25 + "\n"
    for _, question in prompted_questions.items():
        text = question.get("prompted_content")
        if text is None:
            text = multiple_round_splitter.join(question.get("prompted_content_list"))
        text += "\n"
        print(text)
        print("*" * 25)
        final_answers.append(evaluator.generate_answer(question))
        if testcases[question['question_id']].get("correct_answer"):
            final_answers[-1].update({"correct_answer": testcases[question['question_id']]["correct_answer"]})
        print(json.dumps(final_answers[-1], indent=4, ensure_ascii=False))
        print("=" * 25)
        print()
    print("Successfully end evaluation.")
