import re
import torch
import pandas as pd
import concurrent.futures

from tqdm import tqdm
from src.multipipeline import MultiPipeline

def clean_abstract(abstract):
    
    # remove other language
    pos = abstract.find('----')
    if pos > len(abstract) / 3:
        abstract = abstract[:pos]
    
    abstract = re.sub(r'\s+', ' ', abstract)
    abstract = re.sub(r'\\\'', '\'', abstract)
    abstract = re.sub(r'\\\`', '\'', abstract)
    
    # \begin{text}
    abstract = re.sub(r'\\citep?\{([^\}]+)\}', r'', abstract)
    
    # \cite{xxxxxxx}
    abstract = re.sub(r'\\[a-zA-Z]{1,15}\{([^\}]+)\}', r'\1', abstract)
    
    # {\it text}
    abstract = re.sub(r'\{\\[a-zA-Z]{1,15} ([^\}]+)\}', r'\1', abstract)

    # $formula$
    abstract = re.sub(r'\$(.{1,30})\$', r'\1', abstract)
    
    # _{lower_text}
    abstract = re.sub(r'\_\{([^\}]+)\}', r' \1', abstract)
    
    # ^{upper_text}
    abstract = re.sub(r'\^\{([^\}]+)\}', r' \1', abstract)
    
    # abstract = ' '.join(abstract.split()[:400])
    return abstract.strip()

def beautify(text):
    """
    manually beautify t5 output because the spell checker edit our specific name
    return English text in a more beautiful format by following
        1 uppercase first letter of each sentence
        2 remove space in front of full stop
    """
    callback = lambda x: x.group(1).upper()
    text = re.sub(r'^(\w)', callback, text)
    text = re.sub(r' (\. \w)', callback, text)
    text = re.sub(r' \.', '.', text)
    return text


df = pd.read_csv('data/csv/kaggle-arxiv-cscl-2020-12-18.csv')
df.abstract = df.abstract.apply(clean_abstract)

# num_gpus = max(1, torch.cuda.device_count())
num_gpus = 4

pipelines = MultiPipeline(num_gpus)

res = []
BATCH = num_gpus * 2
for i in tqdm(range(len(df) // BATCH + 1)):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_gpus) as executor:
        futures = []
        for abstract in df.abstract.iloc[i * BATCH: (i+1) * BATCH]:
            # args = (abstract, max_length=100, min_length=50)
            futures += [executor.submit(pipelines, abstract, max_length=100, min_length=50)]
    res += [beautify(r.result()[0]['summary_text']) for r in futures]
    
df['summary'] = res

df.to_csv('data/csv/kaggle-arxiv-cscl-2020-12-18-with_summary.csv')