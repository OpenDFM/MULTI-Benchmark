# This README will be deprecated soon as we are preparing our official tutorial version.

# Overview

This folder contains all evaluators to support LLM performance test. Each file contains an evaluator specified to one LLM, and implements a `generate_answer` method to receive a question as input and give out the answer of it.

## Environment preparation before usage

Each evaluator requires its unique environment setting, and a universal environment may not work for all the evaluators. Follow the official guide. If the corresponding model can run well, then so should it fit in our framework.

### Properties for the implemented models

Refer to our [paper](../../docs/static/pdfs/MULTI_Benchmark_v1.3.pdf), section 4.2.

## How to run a test

### Dataset preparation

First, get our dataset from [huggingface](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/). Unzip the files and put them under `data/`.

The structure of `data` should be something like:

```
data
├── images                                       # images folder
├── problem_v1.2.2_20240212_release.json         # MULTI
├── knowledge_v1.2.2_20240212_release.json       # MULTI-Extend
├── hard_list_v1.2.1_20240206.json               # MULTI-Elite
└── captions_v1.2.0_20231217.csv                 # image captions generated by BLIP-6.7b
```

### Arguments for test

`cd eval` at first as the working directory.

We define a lot of arguments in `args.py` and please check there for details. For a quick start, see these examples as reference:

Test Qwen-VL model on the whole dataset, using GPU 0, with images all input, and checkpoint directory specified:
`python eval.py --problem_file ../data/problem_v1.2.2_20240212_release.json  --questions_type 0,1,2,3 --image_type 2 --input_type 2 --model qwen-vl --cuda_device cuda:0 --model_dir QWen/Qwen-VL-Chat` 

The argument `question_type` controls the type of questions to be tested, with 0 for SA, 1 for MA, 2 for FB and 3 for OP, separated with comma. (Abbreviations are defined in our [paper](), section 3.1)

Test VisCPM model on SA, MA and FB on whole dataset also with corresponding knowledge points attached, using GPU 0, with images all input in multiple rounds, and checkpoint directory specified:
`python eval.py --problem_file ../data/problem_v1.2.2_20240212_release.json --knowledge_file ../data/knowledge_v1.2.2_20240212_release.json --questions_type 0,1,2 --input_type 2 --in_turn --model viscpm --cuda_device cuda:0 --model_dir /home/ubuntu/tools/VisCPM/checkpoints`

Test VisualGLM model just on SA questions of MULTI-Elite, using GPU 1, just using pure text as input, using the default checkpoint path on huggingface:
`python eval.py --problem_file ../data/problem_v1.2.2_20240212_release.json --subset ../data/hard_list_v1.2.1_20240206.json --questions_type 0 --input_type 0 --model viscpm --cuda_device cuda:1 --model_dir /home/ubuntu/tools/VisCPM/checkpoints`

Test MOSS model on the whole dataset, using GPU 2, substituting images with corresponding captions, using the defaule checkpoint path on huggingface:
`python eval.py --problem_file ../data/problem_v1.2.2_20240212_release.json --input_type 1 --caption_file ../data/captions_v1.2.0_20231217.csv --model moss --cuda_device cuda:2`

`input_type` is the argument for giving images, with 0 for discarding them, 1 for substituting them with some captions related to the image, and 2 for image input.

All these arguments are independent with each other and can be randomly selected to give expected combinations.


## Implement support for your own model

It's recommended to read the code of the given evaluators before your implementation, implement `generate_answer(self, question:dict)` to match the design supported in `eval.py` and `eval.sh`, which is anticipated to largely ease the coding process. **No forgetting to add their references into `../args.py` for the convenience of usage.**

**It's recommended to execute `model_tester.py` in the parent folder to check the correctness of you implementation. Various problems including implementation errors, small bugs in code, and even wrong environment setting may cause failure of the evaluation. The examples provided in the file cover most kinds of cases presented in our benchmark. Feel free to change the code in it to debug your code😊**

```python
cd ..
python model_tester.py <args> # args are similar to the default setting
```

### Structure of processed questions and answered questions
#### Structure of non-multiple-round QA questions

```
{
    "question_id": <question_id>,
    "question_image_number": int,
    "image_list": [] # optional,
    "prompted_content": <str>
}

# --->

{
    "question_id": <question_id>,
    "question_image_number": int,
    "image_list": [] # optional,
    "input_message": <str>,
    "prediction": <str>
}

```

#### Structure of multiple-round questions

```
{
    "question_id": <question_id>,
    "question_image_number": int,
    "image_list": [],
    "prompted_content_list": []
}

# --->

{
    "question_id": <question_id>,
    "question_image_number": int,
    "image_list": [],
    "input_message_list": [],
    "prediction": <str>
}

```