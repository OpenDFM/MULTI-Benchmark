"""
Some util functions for text manipulation. Maybe deprecated in the future.
"""

import re
from typing import Tuple, List
from PIL import Image
import pdb

MD_PIC_PATTERN = r"!\[\]\(.*?\)"

Question_Type_Dict_zh2en = {
    "单选": "SiC",
    "多选": "MuC",
    "填空": "FillB",
    "解答": "DisQ",
    "其他": "Other",
}

Education_Level_Dict_zh2en = {
    "初中": "JuH",
    "高中": "SeH",
    "大学": "Uni",
    "社会": "Soc",
    "其他": "other",
}


def extract_image_list_from_md(text: str) -> Tuple[str, List[str]]:
    patterns = re.findall(MD_PIC_PATTERN, text)
    for i, pattern in enumerate(patterns):
        subs = f"<img_{i}>"
        text = text.replace(pattern, subs)
    img_list = list(map(lambda s: s[4:-1], patterns))
    return text, img_list


def open_image(image_path, force_blank_return=True):
    try:
        image = Image.open(image_path).convert("RGB")
    except:  # empty string or imageIOError
        if force_blank_return:
            image = Image.new("RGB", (24, 24), (0, 0, 0))  # black placeholder for input
        else:
            image = None
        if image_path != "":
            print(f"WARNING: Image path {image_path} not found. Using black placeholder.")
    return image


def infer_lang_from_question(question):
    question_type = question["question_type"]
    if any("\u4e00" <= ch <= "\u9fff" for ch in question_type):
        return "zh"
    return "en"


if __name__ == "__main__":
    sample = "aaa![](abc.png)bbcd![](tabula.jpg)"
    ret = extract_image_list_from_md(sample)
    ret
