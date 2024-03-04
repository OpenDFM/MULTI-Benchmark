from datasets import load_dataset
import os
import shutil

if os.path.exists("../cache"):
    shutil.rmtree("../cache")
os.makedirs("../cache")

load_dataset("OpenDFM/MULTI-Benchmark", cache_dir="../cache")

random_string = os.listdir("../cache/downloads/extracted")[0]

shutil.copytree(f"../cache/downloads/extracted/{random_string}/", "../data_new/", dirs_exist_ok=True)

shutil.rmtree("../cache")
