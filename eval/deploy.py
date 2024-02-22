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
err = io.StringIO()
app = Flask(__name__)
CORS(app)


args = parse_args_for_score_deploy()
# args.label_file = "../data/problem_v1.2.2_20240212.json"
args.label_file = "../data/problem_final.json"
args.detail = True
args.prediction_dir = "../results"
source_suffix = "/source"
paras_suffix = "/paras"
prediction_file_suffix = "/prediction.json"
prediction_file_name = "prediction.json"
args_file_name = "args.json"
paras_file_suffix = "/paras.json"
source_zip_suffix = "/source.zip"
result_zip_suffix = "/result.zip"


def get_random_dir():
    random_dir = os.path.join(args.prediction_dir, str(uuid.uuid4()))
    os.makedirs(random_dir)
    return random_dir


def save_prediction_json_to_target_dir(json_data, target_dir):
    os.makedirs(target_dir)
    with open(target_dir + prediction_file_suffix, "w") as f:
        json.dump(json_data, f)


def save_paras_to_target_dir(paras_data, target_dir):
    os.makedirs(target_dir)
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
    # get zip file from request
    zip_file_base64 = request.json.get("zip_file", None)
    if zip_file_base64 is None:
        return jsonify({"result": "false", "data": None, "message": "zip_file is None"})

    # generate random dir
    random_dir = get_random_dir()
    source_dir = random_dir + source_suffix
    paras_dir = random_dir + paras_suffix

    # unzip zip file to source dir
    try:
        zip_file_blob = base64.b64decode(zip_file_base64)
        with open(random_dir + source_zip_suffix, "wb") as f:
            f.write(zip_file_blob)
        with zipfile.ZipFile(random_dir + source_zip_suffix, 'r') as zip_ref:
            zip_ref.extractall(source_dir)
        os.remove(random_dir + source_zip_suffix)
    except:
        os.rmdir(random_dir)
        return jsonify({"result": "false", "data": None, "message": "unzip error"})

    # delete all files except prediction.json and args.json in source dir
    for file in os.listdir(source_dir):
        if file != prediction_file_name and file != args_file_name:
            os.remove(os.path.join(source_dir, file))

    # check if prediction.json exists
    if not os.path.exists(source_dir + prediction_file_suffix):
        os.rmdir(random_dir)
        return jsonify({"result": "false", "data": None, "message": "prediction.json not exists"})

    # save request json to paras dir
    paras_json = request.json
    save_paras_to_target_dir(paras_json, paras_dir)

    # change the args
    copy_args = copy.deepcopy(args)
    copy_args.prediction_file = source_dir + prediction_file_suffix

    # run the main function
    with redirect_stdout(output):
        try:
            main(copy_args)
        except Exception as e:
            os.rmdir(random_dir)
            return jsonify({"result": "false", "data": None, "message": str(e)})
    # app.logger.info(output.getvalue())

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
        },
        "message": output.getvalue()
    }

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
