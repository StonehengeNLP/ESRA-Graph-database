# first stage 
FROM python:3.8-slim as builder

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc 
COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir --user -r /requirements.txt

# second stage 
FROM nvidia/cuda:11.2.0-cudnn8-runtime-ubuntu20.04

ENV TZ=Asia/Bangkok \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    apt install --no-install-recommends -y python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local/lib/python3.8/site-packages /usr/local/lib/python3.8/dist-packages

WORKDIR /usr/src/app

RUN python3 -m spacy download en_core_web_sm
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader punkt
RUN python3 -c "from sentence_transformers import SentenceTransformer; _=SentenceTransformer('roberta-large-nli-mean-tokens', cache_folder='./cache_model/')"
RUN python3 -c "from sentence_transformers import SentenceTransformer; _=SentenceTransformer('paraphrase-distilroberta-base-v1', cache_folder='./cache_model/')"
RUN python3 -c "from transformers import T5ForConditionalGeneration; m=T5ForConditionalGeneration.from_pretrained('t5-small'); m.save_pretrained('./cache_model/t5_model')"
RUN python3 -c "from transformers import AutoTokenizer; m=AutoTokenizer.from_pretrained('t5-small'); m.save_pretrained('./cache_model/t5_tok')"

COPY . .

# COPY ./requirements.txt .
# RUN pip install -r requirements.txt
# RUN python -m spacy download en_core_web_sm
# RUN python -m nltk.downloader stopwords
# RUN python -m nltk.downloader punkt
# RUN python -c "from sentence_transformers import SentenceTransformer; _=SentenceTransformer('roberta-large-nli-mean-tokens', cache_folder='./cache_model/')"
# RUN python -c "from sentence_transformers import SentenceTransformer; _=SentenceTransformer('paraphrase-distilroberta-base-v1', cache_folder='./cache_model/')"
# RUN python -c "from transformers import T5ForConditionalGeneration; m=T5ForConditionalGeneration.from_pretrained('t5-small'); m.save_pretrained('./cache_model/t5_model')"
# RUN python -c "from transformers import AutoTokenizer; m=AutoTokenizer.from_pretrained('t5-small'); m.save_pretrained('./cache_model/t5_tok')"

# COPY . .
