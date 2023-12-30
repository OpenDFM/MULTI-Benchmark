import os
from argparse import ArgumentParser
import json


def parse_args():
    parser = ArgumentParser()
    # Add your configurations here ...
    parser.add_argument("--input_list", "-j", type=str, help="selected list in json")
    parser.add_argument(
        "--input_folder",
        "-i",
        type=str,
        help="folder of input, should contain a prediction.json",
    )
    parser.add_argument(
        "--input_dir",
        "-d",
        type=str,
        default="../results",
        help="folder of input whole",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=str,
        default="../selected_results",
        help="folder of output, should contain a prediction.json",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    with open(args.input_list, "r", encoding="utf-8") as f:
        selected_list = json.load(f)
    with open(
        os.path.join(args.input_dir, args.input_folder, "prediction.json"),
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)
    res = {}
    for key in selected_list:
        res.update({key: data[key]})
    output_dir = os.path.join(args.output_dir, args.input_folder)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "prediction.json"), "w", encoding="utf-8") as fw:
        json.dump(res, fw, ensure_ascii=False, indent=4)
