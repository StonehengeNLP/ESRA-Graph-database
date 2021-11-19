import os
import torch

from transformers import pipeline, T5ForConditionalGeneration, AutoTokenizer
from sentence_transformers import SentenceTransformer

def load_sent_trans_model(model_name, device=None):

    is_offline = os.getenv('OFFLINE_SERVER')
    is_offline = True if is_offline=='True' else False
    if is_offline:
        path = f'./cache_model/sentence-transformers_{model_name}'
        model = SentenceTransformer(path, device=device)
    else:
        model = SentenceTransformer(model_name, device=device)
    return model

def load_pipeline(task, model_name, device=-1):

    is_offline = os.getenv('OFFLINE_SERVER')
    is_offline = True if is_offline=='True' else False
    if is_offline:
        # load model: cached T5
        model = T5ForConditionalGeneration.from_pretrained('./cache_model/t5_model')
        # load tokenizer: cached T5
        tokenizer = AutoTokenizer.from_pretrained('./cache_model/t5_tok')
        p = pipeline(task, model=model, tokenizer=tokenizer, device=device)
    else:
        p = pipeline(task, model=model_name, device=device)
    return p
