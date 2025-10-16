# 🖼️ MULTI-Benchmark: Multimodal Understanding Leaderboard with Text and Images

<div align="center">

![MULTI](./docs/static/images/overview.png)

🌐 [网站](https://OpenDFM.github.io/MULTI-Benchmark/) | 📃 [论文](https://arxiv.org/abs/2402.03173/) | 🤗 [数据](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark) | 🏆 [榜单](https://opendfm.github.io/MULTI-Benchmark/#leaderboard) | 📮 [提交](https://wj.sjtu.edu.cn/q/89UmRAJn)

简体中文 | [English](./README.md) 

</div>

## 🔥 新闻

- **[2025.10.16]** 我们发布了 MULTI 中所有问题的标准答案，因为多个模型已经超越了人类专家的基准。现在您可以在本地运行评测并获得最终分数。
- **[2025.9.28]** MULTI 现已在线发布，网址为 [https://doi.org/10.1007/s11432-024-4602-x](https://doi.org/10.1007/s11432-024-4602-x)。
- **[2025.6.22]** MULTI 现已被《中国科学信息科学》多模态大模型专题接收。
- **[2025.1.7]** 我们更新了最新的[榜单](https://opendfm.github.io/MULTI-Benchmark/#leaderboard)。
- **[2025.1.2]** 我们更新了MULTI到v1.3.1。
- **[2024.3.4]** 我们发布了[评测页面](https://opendfm.github.io/MULTI-Benchmark/static/pages/submit.html) (不再维护)。
- **[2024.2.19]** 我们发布了[HuggingFace页面](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/)。
- **[2024.2.6]** 我们在arXiv上发布了我们的[论文](https://arxiv.org/abs/2402.03173/)。
- **[2023.12.7]** 我们发布了我们的基准评测[代码](https://github.com/OpenDFM/MULTI-Benchmark/tree/main/eval)。
- **[2023.12.5]** 我们发布了[GitHub页面](https://OpenDFM.github.io/MULTI-Benchmark/)。

## 📖 介绍

在多模态大型语言模型（MLLMs）快速发展的背景下，如何与人类表现进行比较成为一个重要问题。现有的数据集通常涉及合成的数据或过于简单的任务，而一些模型已经超越了人类专家的基准。本文介绍了**MULTI**，一个源自真实考试问题的中文多模态数据集。**MULTI**包含超过18,000个精心挑选和优化的问题，评估模型在中国现实考试标准下的表现，涵盖了图像-文本理解、复杂推理和知识回忆等方面。此外，我们还引入了**MULTI-Elite**，一个由500个难题组成的精选子集，以及**MULTI-Extend**，一个包含超过4,500个外部知识上下文的数据集，用于测试模型的上下文学习能力。**MULTI**不仅作为一个稳健的评测平台，也为专家级AI的发展指明了道路。

## ⏬ 下载

您只需使用以下命令即可下载数据：

```shell
cd eval
python download_data.py
```

或直接下载 Huggingface 仓库中的[压缩包](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/blob/main/MULTI_v1.3.1_20251016_release.zip)并解压。

`./data` 的结构应该如下所示：

```
./data   
├── images                                       # 包含图片的文件夹
├── problem_v1.3.1_20241210.json                 # MULTI (含答案)
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

您只需要安装另外几个包来运行评测代码：

```shell
pip install tiktoken tqdm rouge_chinese jieba matplotlib
```

如果您只是想为特定设置生成数据（使用`--debug`参数），上面这行代码就是您所需要的一切。

### 运行评测

请参考这些示例以便快速开始：

在MULTI上测试GPT-4o模型，采用多模态输入，并使用MULTI-Extend作为外部知识：

```shell
python eval.py \
  --problem_file ../data/problem_v1.3.1_20241210_release.json \
  --knowledge_file ../data/knowledge_v1.2.2_20240212_release.json \
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
  --problem_file ../data/problem_v1.3.1_20241210_release.json \
  --subset ../data/hard_list_v1.3.0_20241203.json \
  --caption_file ../data/captions_v1.3.1_20241210_points.csv \
  --questions_type 0,1 \
  --image_type 1,2 \
  --input_type 1 \
  --model qwen-vl \
  --model_dir ../models/Qwen-VL-Chat
```

测脚本将在根目录下生成`results`文件夹，结果将保存在`../results/{EXPERIMENT_NAME}`中。评测过程中，脚本将在`../results/{EXPERIMENT_NAME}/checkpoints`中保存检查点，评测完成后您可以删除它们。如果评测被中断，您可以从最后一个检查点继续：

```shell
python eval.py \
  --checkpoint_dir ../results/{EXPERIMENT_NAME}
```

大多数参数都保存在`../results/{EXPERIMENT_NAME}/args.json`中，因此您可以继续评测而无需再次指定所有参数。请注意，出于安全原因，`--api_key`不会保存在`args.json`中，因此您需要再次指定它。

```shell
python eval.py \
  --checkpoint_dir ../results/{EXPERIMENT_NAME} \
  --api_key sk-************************************************
```

有关参数的更多详细信息，请使用`python eval.py -h`并参考`args.py`和`eval.py`。

您可以直接使用我们提供的标准答案对答卷进行评分：

```shell
python metrics.py \
  --label_file ../data/problem_v1.3.1_20241210.json \
  --detail \
  --answer_position end \
  --prediction_file ../results/{EXPERIMENT_NAME}/prediction.json
```

您将会在 `../results/{EXPERIMENT_NAME}` 中看到生成的评分数据。

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


<details>
<summary>您可以直接在本地进行评测</summary>
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
如果您使用我们的官方代码评测模型，可以直接压缩实验结果文件夹`./results/{EXPERIMENT_NAME}`中的预测文件`prediction.json`和配置文件`args.json`为`.zip`格式。

然后，您可以将你的结果提交到我们的[评测页面](https://opendfm.github.io/MULTI-Benchmark/static/pages/submit.html)。
</details>

欢迎拉取请求（Pull Request）并贡献您的代码到我们的评测代码中。我们感激不尽！

**[提示]** 感谢您对 MULTI 数据集的关注！如果您希望将您的模型结果添加至榜单，请填写[此问卷](https://wj.sjtu.edu.cn/q/89UmRAJn)，您的个人信息将被严格保密，请放心填写。🤗

## 📑 引用

如果您觉得我们的工作有用，请引用我们！

```
@article{zhu2025multi,
    title={{MULTI}: Multimodal Understanding Leaderboard with Text and Images}, 
    author={Zichen Zhu and Yang Xu and Lu Chen and Jingkai Yang and Yichuan Ma and Yiming Sun and Hailin Wen and Jiaqi Liu and Jinyu Cai and Yingzi Ma and Situo Zhang and Zihan Zhao and Liangtai Sun and Kai Yu},
    journal = "SCIENCE CHINA Information Sciences",
    year = "2025",
    volume = "68",
    number = "10",
    pages = "200107.1--200107.26",
    doi = "https://doi.org/10.1007/s11432-024-4602-x"
}
```

## 📧 联系我们

如果您有任何问题，请随时通过电子邮件与我们联系： `JamesZhutheThird@sjtu.edu.cn`
