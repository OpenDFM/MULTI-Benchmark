# Overview

This document will guide you to fetch our benchmark.

## Use Google Drive

We directly provide our file in this [link](). This includes a `problem_v1.2.0_20231217.json` containing the benchmark data, and a `knowledge_v1.2.0_20231217.json` containing the knowledge file.

## Use HuggingFace

We also provide our dataset on huggingface. To match the huggingface format, there are some slight changes to the dataset. To get the identical data structure for evaluation, follow the following steps:

```python
from datasets import load_dataset
# load data from huggingface
hf_data = load_dataset("") # TODO: huggingface path here
data, knowledge_data = hf_data["data"], hf_data["kn"]
data = {question["problem_id"]: question for question in data}
knowledge = {kn["knowledge"]: kn for kn in knowledge_data}

import json
with open("xmulti_benchmark.json", "w", encoding="utf-8") as fw: # whatever filename
    json.dump(data, fw, ensure_ascii=False, indent=4)
with open("xmulti_knowledge.json", "w", encoding="utf-8") as fw: # whatever filename
    json.dump(knowledge, fw, ensure_ascii=False, indent=4)

```

and then the output file contains the original format of data.