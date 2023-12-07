# 🖼️ MULTI-Benchmark

<div align="center">

🌐 [Website](https://x-lance.github.io/MULTI-Benchmark/) 

📃 [Paper](https://x-lance.github.io/MULTI-Benchmark/) (Coming Soon) 🤗 [Dataset](https://x-lance.github.io/MULTI-Benchmark/) (Coming Soon) 🎯 [Leaderboard](https://x-lance.github.io/MULTI-Benchmark/) (Coming Soon)

</div>

## 📖 Overview

We introduce **MULTI**: a multi-level, multi-disciplinary, and multi-type cross-modal test benchmark, aimed at evaluating the performance of multimodal generative large models under different conditions and scenarios. We collected and annotated more than 18K questions from exams， quizzes, textbooks, websites and other resources, most of which underwent at least two rounds of human annotation and checking, and three rounds of script cleaning. Some questions were manually adapted to make them more suitable for evaluating the comprehensive ability of the model. These questions involve four educational levels: junior high school, high school, college and social exams, covering Chinese, mathematics, English, physics, chemistry, biology, history, geography, politics, information technology, driving test and other disciplines and fields, including single choice, multiple choice, fill in the blank (given range and fully open), and open-ended discussions.

We manually selected 500 questions to form a difficult subset, which is used to evaluate the model's extreme performance. These questions often contain multiple images and formulas, test the model's comprehensive understanding of multiple images, and require complex and rigorous logical reasoning. The performance of this part of the data will be displayed separately on the leaderboard.

We tested on GPT-3.5 and open-source multimodal large models$^\dagger$, and the results show that even the advanced GPT-3.5 only achieved **43.28%** accuracy, showing a huge room for improvement. We believe that MULTI will motivate the community to build the next generation of multimodal foundation models, to achieve expert-level artificial general intelligence.

$^\dagger$Based on `v0.3.0-20231115` version of the data, tested on SC/MC/FIB three question types.

## 🔥 News 

- **[Coming Soon]** We will soon release our first offical verison of dataset and leaderboard.
- **[2023.12.7]** We release the [code](./eval) of our benchmark evaluation.
- **[2023.12.5]** We release the [GitHub Page](https://x-lance.github.io/MULTI-Benchmark/).

## ⏩ How can I early access MULTI 🤔?

We will release our first official version soon.

Please feel free to contact (`JamesZhutheThird@sjtu.edu.cn`) and keep in touch with us. 

## 📑 Citation

If you find our work useful, please consider citing us!

```
@misc{zhu2023multibench,
      title={MULTI: Multimodal Understanding Leaderboard with Text and Images},
      author={Zichen Zhu, Yang Xu, Lu Chen, Jingkai Yang, Yichuan Ma, Yimin Sun, Hailin Wen, Jiaqi Liu, Jinyu Cai, Yingzi Ma, Liangtai Sun, Zihan Zhao, and Kai Yu},
      year={2023},
      howpublished = "\url{https://github.com/X-LANCE/MULTI-Benchmark}",
}
```

## 📧 Contact Us

If you would like to early access our benchmark or have any questions, please feel free to contact: `JamesZhutheThird@sjtu.edu.cn`