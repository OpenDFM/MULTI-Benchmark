import base64
import copy
import os
import uuid
from metrics import *
from args import parse_args_for_score_deploy
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
from contextlib import redirect_stdout
import zipfile

# redirect stdout to string
output = io.StringIO()
app = Flask(__name__)
CORS(app)


args = parse_args_for_score_deploy()
# args.label_file = "../data/problem_v1.2.2_20240212.json"
args.label_file = "../data/problem_final.json"
args.detail = True
args.prediction_dir = "../results"
source_suffix = "/source"
prediction_file_suffix = "/prediction.json"
paras_file_suffix = "/paras.json"
result_zip_suffix = "/result.zip"


def get_random_dir():
    return os.path.join(args.prediction_dir, str(uuid.uuid4()))


def save_prediction_json_to_target_dir(json_data, target_dir):
    os.makedirs(target_dir)
    with open(target_dir + prediction_file_suffix, "w") as f:
        json.dump(json_data, f)


def save_paras_to_target_dir(paras_data, target_dir):
    with open(target_dir + paras_file_suffix, "w") as f:
        json.dump(paras_data, f)


def zip_dir(directory, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))


# generate all


@app.route("/generate", methods=["POST"])
def generate():
    prediction_json = request.json.get("prediction_json", None)
    if prediction_json is None:
        return jsonify({"result": "false", "data": None})

    # generate random dir
    random_dir = get_random_dir()
    source_dir = random_dir + source_suffix

    # save prediction json to random dir
    save_prediction_json_to_target_dir(json.loads(
        prediction_json["fileContent"]), source_dir)
    prediction_file = source_dir + prediction_file_suffix

    # save request json too
    paras_json = request.json
    save_paras_to_target_dir(paras_json, source_dir)

    # change the args
    copy_args = copy.deepcopy(args)
    copy_args.prediction_file = prediction_file

    # run the main function
    with redirect_stdout(output):
        main(copy_args)
    app.logger.info(output.getvalue())

    # zip the dir
    zip_dir(source_dir, random_dir + result_zip_suffix)

    # read the file
    with open(random_dir + result_zip_suffix, 'rb') as result_zip_file:
        result_zip_file_blob = result_zip_file.read()
    result_zip_base64 = base64.b64encode(result_zip_file_blob).decode('utf-8')

    # return the file
    response_data = {
        "result": "true",
        "data": {
            "zip_file": result_zip_base64,
            "other": {
                "somthing": "else"
            }
        }
    }

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
