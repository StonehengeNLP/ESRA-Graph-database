import nltk
from nltk.tokenize import sent_tokenize 

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
  
import re
import torch
from transformers import pipeline
from .graph_database import GraphDatabase


gdb = GraphDatabase()
device = 0 if torch.cuda.is_available() else -1
bart_base = pipeline("summarization", model='t5-small', device=device)

def is_include_word(word, text):
    return re.search(r'\b{}\b'.format(word), text, flags=re.IGNORECASE)

def filtered_summarization(keys, title, abstract):
    """
    This explanation method is to filter some sentences that include keyword(s)
    and then throw it into summarization model (we use t5-small in this case)
    so, we will get our explanation that based on entities in the path from keywords to paper
    Although it looks like summarization, it is also explanation of the local graph as well.
    """
    
    nodes = gdb.get_related_nodes(keys, title)
    
    sentences = sent_tokenize(abstract)
    
    selected_sentence = []
    for sentence in sentences:
        for name in nodes + keys:
            if is_include_word(name, sentence):
                selected_sentence += [sentence]
                break
            
    new_sentence = ' '.join(selected_sentence)
    summ = bart_base(new_sentence, max_length=100, min_length=50)[0]['summary_text']

    return summ