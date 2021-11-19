import time
import torch
from transformers import pipeline

from transformers import pipeline, T5ForConditionalGeneration, AutoTokenizer

# import load cached model function
import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from offline_setup_util import load_pipeline

# def load_pipeline(task, model_name, device=-1):
#     is_offline = os.getenv('OFFLINE_SERVER')
#     is_offline = True if is_offline=='True' else False
#     if is_offline:
#         # load model: cached T5
#         model = T5ForConditionalGeneration.from_pretrained('../cache_model/t5_model')
#         # load tokenizer: cached T5
#         tokenizer = AutoTokenizer.from_pretrained('../cache_model/t5_tok')
#         p = pipeline(task, model=model, tokenizer=tokenizer, device=device)
#     else:
#         p = pipeline(task, model=model_name, device=device)
#     return p

class MultiPipeline:
    
    def __init__(self, num_pipes=None):
        if torch.cuda.is_available():
            if num_pipes is None:
                self.num_pipes = torch.cuda.device_count()
            else:
                self.num_pipes = num_pipes
            # self.pipelines = [pipeline("summarization", model='t5-small', device=i) for i in range(self.num_pipes)]
            self.pipelines = [load_pipeline("summarization", 't5-small', device=i) for i in range(self.num_pipes)]
            print(f'>>>> Initialize {self.num_pipes} pipelines with GPUs')
        else:
            self.num_pipes = 1
            # self.pipelines = [pipeline("summarization", model='t5-small', device=-1)]
            self.pipelines = [load_pipeline("summarization", 't5-small', device=-1)]
            print('>>>> Initialize 1 pipelines with CPU')

        self.locks = [0] * self.num_pipes
        
    def __call__(self, *args, **kwargs):
        MAX_RETRIES = 20
        retries = 0
        while True:
            if retries >= MAX_RETRIES:
                for i in range(self.num_pipes):
                    self.locks[i] = 0
                raise Exception('Exceed maximum retries')
            for i in range(self.num_pipes):
                if self.locks[i] == 0:
                    self.locks[i] = 1
                    result = self.pipelines[i](*args, **kwargs)
                    self.locks[i] = 0
                    return result
            time.sleep(0.5)
            retries += 1

