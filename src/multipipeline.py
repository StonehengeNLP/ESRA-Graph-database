import time
import torch
from transformers import pipeline
from transformers import BartTokenizer, BartForConditionalGeneration


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
            # self.pipelines = [pipeline("summarization", model='t5-small', device=-1)]
            self.pipelines = [self._get_pipeline(device='cpu')]
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

    def _get_pipeline(self, device):        
        tokenizer = BartTokenizer.from_pretrained("sshleifer/distilbart-cnn-6-6")
        model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-6-6").to(device)

        def summarize(article, **kwargs):
            batch = tokenizer(article, truncation=True, padding='longest', return_tensors="pt").to(device)
            translated = model.generate(
                **batch, 
                **kwargs,
                num_beams=5,
                )
            summary = tokenizer.batch_decode(translated, skip_special_tokens=True)
            return summary[0]
        
        return summarize