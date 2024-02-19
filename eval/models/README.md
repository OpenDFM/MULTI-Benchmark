# this README will be deprecated soon

# Overview

This folder contains all evaluators to support LLM performance test. Each file contains an evaluator specified to one LLM, and implements a `generate_answer` method to receive a question as input and give out the answer of it.

## Environment preparation before usage

Each evaluator requires its unique environment setting, and a universal environment may not work for all the evaluators.

### Support for MOSS

```
conda create -n moss python=3.9 -y
conda activate moss
pip install transformers==4.32.0 # Too high level of transformer version causes issue
pip install torch accelerate
pip install modelscope # to use modelscope
```

### For Qwen
```
conda create -n qwen python=3.9 -y
conda activate qwen
pip install torch transformers torchvision accelerate matplotlib tiktoken transformers_stream_generator
pip install modelscope # to use modelscope
pip install optimum auto-gptq # for quantize support
```

### For VisCPM

Follow the official guide. For convenience, set up a new environment.
```
git clone https://github.com/OpenBMB/VisCPM.git
cd VisCPM
conda create -n viscpm python=3.10 -y
conda activate viscpm
pip install -r requirements.txt
pip install bminf # for quantize support
```

### For VisualGLM
Modify on the environment `moss` here for convenience.
```
pip install SwissArmyTransformer peft torchvision
```
Note [Issue](https://github.com/THUDM/ChatGLM-6B/issues/212) here.


### Properties for the implemented models
| Model | Puretext\* | One-image | Multiple-images-a-time\*\* |
|:-:|:-:|:-:|:-:|
| Qwen-VL | ✅ | ✅ | ✅ |
| VisCPM | ❌ | ✅ | ❌ |
| VisualGLM | ✅ | ✅ | ❌ |
| MOSS | ✅ | ❌ | ❌ |

\* If not supported, a black blank image is needed to pass into the image tokenizer when dealing with the pure texts. 

\*\* If not supported, it'll be required to use multiple rounds of dialogue to pass multiple images. Add the argument `--in_turn` when adopting image inputs.

**Note. In the current Qwen-VL, multiple images a time actually performs very poor, so we prefer using multiple rounds.**

## Implement support for your own model

It's recommended to read the code of the given evaluators before your implementation, implement `generate_answer(self, question:dict)` to match the design supported in `eval.py` and `eval.sh`, which is anticipated to largely ease the coding process. Remember to add their references into `../args.py` for the convenience of usage.

**It's recommended to execute `model_tester.py` in the parent folder to check the correctness of you implementation. Various problems including implementation errors, small bugs in code, and even wrong environment setting may cause failure of the evaluation. Feel free to change the code in it to debug your code😊**

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