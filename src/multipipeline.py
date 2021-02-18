import time
import torch
from transformers import pipeline

class MultiPipeline:
    
    def __init__(self, num_pipes=None):
        if torch.cuda.is_available():
            if num_pipes is None:
                self.num_pipes = torch.cuda.device_count()
            else:
                self.num_pipes = num_pipes
            self.pipelines = [pipeline("summarization", model='t5-small', device=i) for i in range(self.num_pipes)]
            print(f'>>>> Initialize {self.num_pipes} pipelines with GPUs')
        else:
            self.num_pipes = 1
            self.pipelines = [pipeline("summarization", model='t5-small', device=-1)]
            print('>>>> Initialize 1 pipelines with CPU')

        self.locks = [0] * self.num_pipes
        
    def __call__(self, *args, **kwargs):
        MAX_RETRIES = 20
        retries = 0
        while True:
            if retries >= MAX_RETRIES:
                raise Exception('Exceed maximum retries')
            for i in range(self.num_pipes):
                if self.locks[i] == 0:
                    self.locks[i] = 1
                    result = self.pipelines[i](*args, **kwargs)
                    self.locks[i] = 0
                    return result
            time.sleep(0.5)
            retries += 1
