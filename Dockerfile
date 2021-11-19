FROM python:3.8

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader punkt
RUN python -c "from sentence_transformers import SentenceTransformer; _=SentenceTransformer('roberta-large-nli-mean-tokens', cache_folder='./cache_model/')"
RUN python -c "from sentence_transformers import SentenceTransformer; _=SentenceTransformer('paraphrase-distilroberta-base-v1', cache_folder='./cache_model/')"
RUN python -c "from transformers import T5ForConditionalGeneration; m=T5ForConditionalGeneration.from_pretrained('t5-small'); m.save_pretrained('./cache_model/t5_model')"
RUN python -c "from transformers import AutoTokenizer; m=AutoTokenizer.from_pretrained('t5-small'); m.save_pretrained('./cache_model/t5_tok')"



COPY . .

# CMD [ "echo", "serviceUp" ]
# CMD [ "./wait-for-neo4j.sh" ]
# CMD [ "./start.sh" ]
# CMD [ "python", "add_data.py" ]
# CMD [ "python", "cluster_and_drop.py" ]
# CMD [ "python", "gen_vocab.py" ]
# CMD [ "python", "app.py" ]