# 🖼️ MULTI-Benchmark: Multimodal Understanding Leaderboard with Text and Images

<div align="center">

![MULTI](./docs/static/images/overview.png)

🌐 [网站](https://OpenDFM.github.io/MULTI-Benchmark/) | 📃 [论文](https://arxiv.org/abs/2402.03173/) | 🤗 [数据](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark) | 🎯 [榜单]() (即将上线) 

简体中文 | [English](./README.md) 

</div>

## 🔥 新闻

- **[即将上线]** 我们将发布官方评估平台。
- **[2024.2.19]** 我们发布了[HuggingFace页面](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/)。
- **[2024.2.6]** 我们在arXiv上发布了我们的[论文](https://arxiv.org/abs/2402.03173/)。
- **[2023.12.7]** 我们发布了我们的基准评估[代码](./eval)。
- **[2023.12.5]** 我们发布了[GitHub页面](https://OpenDFM.github.io/MULTI-Benchmark/)。

## 📖 介绍

在多模态大型语言模型（MLLMs）迅速进步的背景下，提出具有挑战性且符合现实场景的基准测试变得尤为重要，而现有的基准测试主要关注于理解简单的自然图像和短文本。在本文中，我们介绍了***MULTI***，作为一个前沿的基准测试，用于评估MLLMs在理解复杂的表格和图像、以及进行长文本推理的能力。**MULTI**提供多模态输入，并要求回答是精确的或开放式的，反映了现实生活中的考试风格。**MULTI**包括超过 18,000 个问题，挑战MLLMs进行多种任务，从公式推导到图像细节分析和跨模态推理。我们还引入了***MULTI-Elite***，一个精心挑选的包含500个问题的难题子集，以及***MULTI-Extend***，包含超过 4,500 个外部知识上下文。我们的评估显示了MLLMs进步的巨大潜力，GPT-4V在**MULTI**上的准确率达到了 **63.7%**，而其他MLLMs的得分介于 **28.5%** 和 **55.3%** 之间。**MULTI**不仅作为一个稳健的评估平台，也为专家级AI的发展指明了道路。

## 🏆 Leaderboard

| 模态 |     模型      | 版本                       | 总体 | MULTI-Elite |
|:----:|:-------------:| -------------------------- |:----:|:-----------:|
|  🖼️  |    GPT-4V     | gpt-4-vision-preview       | 63.7 |    14.0     |
|  🖼️  |     Yi-VL     | Yi-34B-Chat                | 55.3 |    26.2     |
|  🖼️  | Gemini Vision | gemini-pro-vision          | 53.7 |    12.4     |
|  📃  |    Gemini     | gemini-pro                 | 52.2 |    10.5     |
|  📃  |     GPT-4     | gpt-4-1106-preview         | 50.2 |     5.8     |
|  📃  |    DFM-2.0    | dfm-2.0-70b-preview        | 49.7 |    18.0     |
|  🖼️  |   InternVL    | InternVL-Chat-Chinese-V1.1 | 44.9 |    20.7     |
|  🖼️  |    Qwen-VL    | Qwen-VL-Chat               | 39.0 |    10.5     |
|  📃  |    ChatGPT    | gpt-3.5-turbo-1106         | 35.9 |     4.7     |
|  🖼️  |    VisCPM     | VisCPM-Chat                | 33.4 |    13.0     |
|  📃  |     MOSS      | moss-moon-003-sft          | 32.6 |    13.1     |
|  🖼️  |   VisualGLM   | visualglm-6b               | 31.1 |    12.8     |
|  🖼️  | Chinese-LLaVA | Chinese-LLaVA-Cllama2      | 28.5 |    12.3     |

更多详情，请访问我们的[排行榜]()（即将推出）。

## ⏬ 下载

你可以从[HuggingFace页面](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark)下载数据集。最新[版本](https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/blob/main/MULTI_v1.2.2_20240212_release.zip)为`v1.2.2`。

```
wget https://huggingface.co/datasets/OpenDFM/MULTI-Benchmark/resolve/main/MULTI_v1.2.2_20240212_release.zip
unzip MULTI_v1.2.2_20240212_release.zip -d ./data
```

## 📝 如何评估

此部分即将更新。现在，请参考[历史版本README](./eval/models/README.md)。

## 📮 如何提交

你需要首先准备一个UTF-8编码的JSON文件，格式如下：

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
如果你使用我们的官方代码评估模型，你可以直接压缩实验结果文件夹`./results/EXPERIMENT_NAME`。

然后，你可以将你的结果提交到我们的[评估平台]()（即将推出）。

感谢您对 MULTI 数据集的关注！由于自动评测平台尚未上线，请填写[此问卷](https://wj.sjtu.edu.cn/q/89UmRAJn)以获取评测结果，您的个人信息将被严格保密，请放心填写。🤗

欢迎拉取请求（Pull Request）并贡献你的代码到我们的评估代码中。我们感激不尽！

## 📑 引用

如果你觉得我们的工作有用，请引用我们！

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

如果你有任何问题，请随时通过电子邮件联系我们 `JamesZhutheThird@sjtu.edu.cn` 和 `xuyang0112@sjtu.edu.cn`
