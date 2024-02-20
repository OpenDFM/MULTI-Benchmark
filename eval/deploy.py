import copy
import os
import uuid
from metrics import *
from args import parse_args_for_score_deploy

from flask import Flask, request, jsonify


app = Flask(__name__)

args = parse_args_for_score_deploy()


prediction_file_suffix = "/prediction.json"
result_file_suffix = "/result.json"


def save_prediction_json_to_random_dir(json_data):
    random_dir = os.path.join(args.prediction_dir, str(uuid.uuid4()))
    os.makedirs(random_dir)
    with open(random_dir + prediction_file_suffix, "w") as f:
        json.dump(json_data, f)
    return random_dir


def save_result_to_target_dir(result, target_dir):
    with open(target_dir + result_file_suffix, "w") as f:
        json.dump(result, f)


# generate all


@app.route("/generate", methods=["POST"])
def generate():
    prediction_json = request.json["prediction_json"]
    if prediction_json is None:
        return jsonify({"result": "false"})
    prediction_file = save_prediction_json_to_random_dir(prediction_json)
    result_json = request.json
    save_result_to_target_dir(result_json, prediction_file)
    copy_args = copy.deepcopy(args)
    copy_args.prediction_file = prediction_file
    main(copy_args)
    return jsonify({"result": "true"})


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
