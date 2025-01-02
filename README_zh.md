# 🖼️ MULTI-Benchmark: Multimodal Understanding Leaderboard with Text and Images

<div align="center">

![MULTI](./docs/static/images/overview.png)

🌐 [网站](https://OpenDFM.github.io/MULTI-Benchmark/) | 📃 [论文](https://arxiv.org/abs/2402.03173/) | 🤗 [数据](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark) | 📮 [提交](https://opendfm.github.io/MULTI-Benchmark/static/pages/submit.html)

简体中文 | [English](./README.md) 

</div>

## 🔥 新闻

- **[2024.3.4]** 我们发布了[评测页面](https://opendfm.github.io/MULTI-Benchmark/static/pages/submit.html)。
- **[2024.2.19]** 我们发布了[HuggingFace页面](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/)。
- **[2024.2.6]** 我们在arXiv上发布了我们的[论文](https://arxiv.org/abs/2402.03173/)。
- **[2023.12.7]** 我们发布了我们的基准评测[代码](https://github.com/OpenDFM/MULTI-Benchmark/tree/main/eval)。
- **[2023.12.5]** 我们发布了[GitHub页面](https://OpenDFM.github.io/MULTI-Benchmark/)。

## 📖 介绍

在多模态大型语言模型（MLLMs）迅速进步的背景下，提出具有挑战性且符合现实场景的基准测试变得尤为重要，而现有的基准测试主要关注于理解简单的自然图像和短文本。在本文中，我们介绍了***MULTI***，作为一个前沿的基准测试，用于评测MLLMs在理解复杂的表格和图像、以及进行长文本推理的能力。**MULTI**提供多模态输入，并要求回答是精确的或开放式的，反映了现实生活中的考试风格。**MULTI**包括超过 18,000 个问题，挑战MLLMs进行多种任务，从公式推导到图像细节分析和跨模态推理。我们还引入了***MULTI-Elite***，一个精心挑选的包含500个问题的难题子集，以及***MULTI-Extend***，包含超过 4,500 个外部知识上下文。我们的评测显示了MLLMs进步的巨大潜力，GPT-4V在**MULTI**上的准确率达到了 **63.7%**，而其他MLLMs的得分介于 **28.5%** 和 **55.3%** 之间。**MULTI**不仅作为一个稳健的评测平台，也为专家级AI的发展指明了道路。

## ⏬ 下载

您只需使用以下命令即可下载数据：

```shell
cd eval
python download_data.py
```

`./data` 的结构应该如下所示：

```
./data   
├── images                                       # 包含图片的文件夹
├── problem_v1.3.1_20241210_release.json         # MULTI
├── knowledge_v1.2.2_20240212_release.json       # MULTI-Extend
├── hard_list_v1.3.0_20241203.json               # MULTI-Elite
├── captions_v1.3.1_20241210_blip.csv            # 由BLIP-6.7b生成的图片描述
├── captions_v1.3.1_20241210_points.csv          # 由POINTS-1-5生成的图片描述
├── ocr_v1.3.1_20241210_easyocr.csv              # 由EasyOCR生成的OCR数据
└── ocr_v1.3.1_20241210_points.csv               # 由POINTS-1-5生成的OCR数据
```

## 📝 如何评测

我们在`eval`中提供了一个统一的评测框架。`eval/models`中的每个文件都包含了一个针对某个M/LLM的评测器，并实现了一个`generate_answer`方法来接收问题输入并输出答案。

```shell
cd eval
python eval.py -h # 列出所有支持的参数
python eval.py -l # 列出所有支持的模型
```

### 使用前的环境准备

每个模型都需要其独特的环境设置，通用环境可能不适用于所有模型的评测。**按照官方文档操作即可。** 如果相应的模型运行良好，那么它应该也适合我们的框架。

您只需要安装另外两个包来运行评测代码：

```shell
pip install tiktoken tqdm
```

如果您只是想为特定设置生成数据（使用`--debug`参数），上面这行代码就是您所需要的一切。

### 运行评测

请参考这些示例以便快速开始：

在MULTI上测试GPT-4o模型，采用多模态输入，并使用MULTI-Extend作为外部知识：

```shell
python eval.py \
  --problem_file ../data/problem_{version}.json \
  --knowledge_file ../data/knowledge_{version}.json \
  --questions_type 0,1,2,3 \
  --image_type 0,1,2 \
  --input_type 2 \
  --model gpt-4o \
  --model_version gpt-4o-latest \
  --api_key sk-************************************************
```

在MULTI-Elite上测试Qwen-VL模型，使用图片描述输入，跳过所有不包含图片的问题，仅评测选择题，自动设置cuda设备：

```shell
python eval.py \
  --problem_file ../data/problem_{version}.json \
  --subset ../data/hard_list_{version}.json \
  --caption_file ../data/captions_{version}.csv \
  --questions_type 0,1 \
  --image_type 1,2 \
  --input_type 1 \
  --model qwen-vl \
  --model_dir ../models/Qwen-VL-Chat
```

测脚本将在根目录下生成`results`文件夹，结果将保存在`../results/EXPERIMENT_NAME`中。评测过程中，脚本将在`../results/EXPERIMENT_NAME/checkpoints`中保存检查点，评测完成后您可以删除它们。如果评测被中断，您可以从最后一个检查点继续：

```shell
python eval.py \
  --checkpoint_dir ../results/EXPERIMENT_NAME
```

大多数参数都保存在`../results/EXPERIMENT_NAME/args.json`中，因此您可以继续评测而无需再次指定所有参数。请注意，出于安全原因，`--api_key`不会保存在`args.json`中，因此您需要再次指定它。

```shell
python eval.py \
  --checkpoint_dir ../results/EXPERIMENT_NAME \
  --api_key sk-************************************************
```

有关参数的更多详细信息，请使用`python eval.py -h`并参考`args.py`和`eval.py`。

### 为您的模型增加支持

建议在此之前阅读`eval/models`中其他评测器的代码。

创建`class YourModelEvaluator`并实现 `generate_answer(self, question:dict)`以匹配`eval.py`和`eval.sh`中支持的设计，这预计将大大简化代码实现过程。

**不要忘记将它们的调用方式添加到`args.py`中，以方便使用。**

您可以在`eval`文件夹中执行`model_tester.py`来检查您的实现的正确性。各种问题，包括实现错误、代码中的小错误，甚至错误的环境设置都可能导致评测失败。文件中提供的示例覆盖了我们基准测试中呈现的大多数情况类型。随意更改其中的代码以调试您的代码😊

```shell
python model_tester.py <args> # args 类似于上面的默认设置
```

### 为图片创建描述和OCR数据

为图片生成描述或OCR数据，并以下面的格式保存在csv中：

```
../data/images/czls/502_1.png,a cartoon drawing of a man standing in front of a large block
../data/images/czls/525_1.png,a chinese newspaper with the headline, china's new year
...
```

我们提供了两个示例脚本来为图片生成标题（`image_caption.py`）和OCR数据（`image_ocr.py`）。

## 📮 如何提交

您需要首先准备一个UTF-8编码的JSON文件，格式如下：

```
{
    "czsx_0_0": {
        "question_id": "czsx_0_0",
        "question_image_number": 1,
        "image_list": [...],
        "input_message": ...,
        "prediction": "C"
    },
    ...
}
```
如果您使用我们的官方代码评测模型，可以直接压缩实验结果文件夹`./results/EXPERIMENT_NAME`中的预测文件`prediction.json`和配置文件`args.json`为`.zip`格式。

然后，您可以将你的结果提交到我们的[评测页面](https://opendfm.github.io/MULTI-Benchmark/static/pages/submit.html)。

欢迎拉取请求（Pull Request）并贡献您的代码到我们的评测代码中。我们感激不尽！

**[提示]** 感谢您对 MULTI 数据集的关注！如果您希望将您的模型结果添加至榜单，请填写[此问卷](https://wj.sjtu.edu.cn/q/89UmRAJn)，您的个人信息将被严格保密，请放心填写。🤗

## 📑 引用

如果您觉得我们的工作有用，请引用我们！

```
@misc{zhu2024multi,
      title={{MULTI}: Multimodal Understanding Leaderboard with Text and Images}, 
      author={Zichen Zhu and Yang Xu and Lu Chen and Jingkai Yang and Yichuan Ma and Yiming Sun and Hailin Wen and Jiaqi Liu and Jinyu Cai and Yingzi Ma and Situo Zhang and Zihan Zhao and Liangtai Sun and Kai Yu},
      year={2024},
      eprint={2402.03173},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## 📧 联系我们

如果您有任何问题，请随时通过电子邮件与我们联系： `JamesZhutheThird@sjtu.edu.cn` 和 `xuyang0112@sjtu.edu.cn`
