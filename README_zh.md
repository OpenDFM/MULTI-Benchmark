# MULTI

MULTI: Multimodal Understanding Leaderboard with Text and Images
多层次、多学科、多题型的跨模态测试基准

## 作者

Zichen Zhu, Yang Xu, Lu Chen, Jingkai Yang, Yichuan Ma, Yimin Sun, Hailin Wen, Jiaqi Liu, Jinyu Cai, Yingzi Ma, Liangtai Sun, Zihan Zhao, Kai Yu

X-LANCE Lab, Department of Computer Science and Engineering

MoE Key Lab of Artificial Intelligence, SJTU AI Institute

Shanghai Jiao Tong University, Shanghai, China


`{JamesZhutheThird, xuyang0112, chenlusz, kai.yu}@sjtu.edu.cn`

## 链接

Website `https://x-lance.github.io/MULTI-Benchmark/`

Github `https://github.com/X-LANCE/MULTI-Benchmark`

Huggingface 即将公开

arXiv 即将公开

## 简介

我们介绍 **MULTI**：这是一个多层次、多学科、多题型的跨模态测试基准，旨在评估多模态生成式大模型在不同条件和场景下的性能。我们从考试、测验、教材、网站等教学资源中收集并整理了超过 18K 道题目，其中绝大部分题目经过不少于两轮的人工标注校对，和三轮脚本清洗，部分题目经过人工改编，使其更适合于对模型综合能力的评测。这些问题涉及初中、高中、大学和社会考试四个教育层次，涵盖语文、数学、英语、物理、化学、生物、历史、地理、政治、信息技术、驾考等多个学科和领域，包含 单项选择、多项选择、填空题（给定范围与完全开放）、和开放式解答题等。

我们人工挑选出五百道题目，构成困难子集，用于评测模型的极限性能。这些题目往往包含多张图片和公式，考察模型对多个图片的综合理解，并要求复杂而严谨的逻辑推理。这部分数据的成绩将会单独在榜单中展示。

我们在GPT-3.5，和开源多模态大模型上进行测试$^*$，结果表明，即使是先进的 GPT-3.5 也只达到了 **43.28%** 的准确率，展示出巨大的改进空间。我们相信，MULTI 将激励社区建立下一代多模态基础模型，以实现专家级人工通用智能。

$^*$ 基于 `v0.3.0-20231115` 版本的数据，在SC/MC/FIB三个题型上进行测试。

### 数据展示

即将上线

### 对比

即将上线

### 样例分析

即将上线

## 榜单

提交平台和自动评测脚本即将上线

## 联系我们

如果您想提前在我们的基准测试上进行测试或有任何疑问，请随时联系`JamesZhutheThird@sjtu.edu.cn`
