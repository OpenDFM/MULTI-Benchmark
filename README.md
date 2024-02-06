# 🖼️ MULTI-Benchmark

<div align="center">

🌐 [Website](https://opendfm.github.io/MULTI-Benchmark/) 

📃 [Paper](https://arxiv.org/abs/2402.03173/) 

🤗 [Dataset](https://opendfm.github.io/MULTI-Benchmark/) (Coming Soon) 

🎯 [Leaderboard](https://opendfm.github.io/MULTI-Benchmark/) (Coming Soon)

</div>

# MULTI-Benchmark

[This](https://OpenDFM.github.io/MULTI-Benchmark/) is our official page.

## 🔥 News 

- **[Coming Soon]** We will soon release our first offical verison of dataset and leaderboard.
- **[2024.2.6]** We publish our [paper](https://arxiv.org/abs/2402.03173/) on arXiv.
- **[2023.12.7]** We release the [code](./eval) of our benchmark evaluation.
- **[2023.12.5]** We release the [GitHub Page](https://opendfm.github.io/MULTI-Benchmark/).

## 📖 Overview

We introduce **MULTI**: a multi-level, multi-disciplinary, and multi-type cross-modal test benchmark, aimed at evaluating the performance of multimodal generative large models under different conditions and scenarios. We collected and annotated more than 18K questions from exams，quizzes, textbooks, websites and other resources, most of which underwent at least two rounds of human annotation and checking, and three rounds of script cleaning. Some questions were manually adapted to make them more suitable for evaluating the comprehensive ability of the model. These questions involve four educational levels: junior high school, high school, college and social exams, covering Chinese, mathematics, English, physics, chemistry, biology, history, geography, politics, information technology, driving test and other disciplines and fields, including single choice, multiple choice, fill in the blank (given range and fully open), and open-ended discussions.

We manually selected 500 questions to form a difficult subset, which is used to evaluate the model's extreme performance. These questions often contain multiple images and formulas, test the model's comprehensive understanding of multiple images, and require complex and rigorous logical reasoning. The performance of this part of the data will be displayed separately on the leaderboard.

We tested on GPT-3.5 and open-source multimodal large models $^\dagger$ , and the results show that even the advanced GPT-3.5 only achieved **43.28%** accuracy, showing a huge room for improvement. We believe that MULTI will motivate the community to build the next generation of multimodal foundation models, to achieve expert-level artificial general intelligence.

$^\dagger$ Based on `v0.3.0-20231115` version of the data, tested on SC/MC/FIB three question types.

## ⏩ How can I early access MULTI 🤔?

We will release our first official version soon. (Within this week)

Please feel free to contact (`JamesZhutheThird@sjtu.edu.cn` and `xuyang0112@sjtu.edu.cn`) and keep in touch with us. 

## 📑 Citation

If you find our work useful, please consider citing us!

```
@misc{zhu2024multi,
      title={MULTI: Multimodal Understanding Leaderboard with Text and Images}, 
      author={Zichen Zhu and Yang Xu and Lu Chen and Jingkai Yang and Yichuan Ma and Yiming Sun and Hailin Wen and Jiaqi Liu and Jinyu Cai and Yingzi Ma and Situo Zhang and Zihan Zhao and Liangtai Sun and Kai Yu},
      year={2024},
      eprint={2402.03173},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## 📧 Contact Us

If you would like to early access our benchmark or have any questions, please feel free to contact: `JamesZhutheThird@sjtu.edu.cn` and `xuyang0112@sjtu.edu.cn`

