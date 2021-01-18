import nltk
from nltk.tokenize import sent_tokenize 

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
  
import re
import torch
from functools import lru_cache
from transformers import pipeline
from .graph_database import GraphDatabase


gdb = GraphDatabase()

device = 0 if torch.cuda.is_available() else -1
t5_small = pipeline("summarization", model='t5-small', device=device)


def is_include_word(word, text):
    """ 
    return true if the word is included in the text
    
    I have handled plural cases by adding just 's' and 'es'
    you could make it smarter :D
    """
    return re.search(r'\b{}(s|es){{0,1}}\b'.format(word), text, flags=re.IGNORECASE)

def count_word(text):
    """
    return number of English word exists in the given text 
    """
    return len(re.findall('\w+', text))

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

@lru_cache(maxsize=128)
def _summarize(sentence, max_length, min_length):
    """
    this function is for summarizing sentences
    """
    summ = t5_small(sentence, max_length=100, min_length=min_length)[0]['summary_text']
    summ = beautify(summ)
    return summ

def filtered_summarization(keys, title, abstract):
    """
    This explanation method is to filter some sentences that include keyword(s)
    and then throw it into summarization model (we use t5-small in this case)
    so, we will get our explanation that based on entities in the path from keywords to paper
    Although it looks like summarization, it is also explanation of the local graph as well.
    
    This filter sentences by
    1. nodes between path from keywords to paper
    2. search keys
    3. static list of words
    
    NOTE: Now, I have repeated sentences that contains multiple keywords
    so, the model can know that the sentences are important and put it in summarization
    
    If some cases are very strange, this should has fixed
    """
    
    nodes = gdb.get_related_nodes(tuple(keys), title)
    filter_words = nodes + keys + ['we', 'our', 'in this paper']
    
    sentences = sent_tokenize(abstract)
    
    selected_sentence = []
    for sentence in sentences:
        for name in filter_words:
            if is_include_word(name, sentence):
                selected_sentence += [sentence]
                # break
            
    new_sentence = ' '.join(selected_sentence)
    word_count = count_word(new_sentence)
    # print(new_sentence)

    if word_count > 10:
        min_length = min(50, word_count)
        summ = _summarize(new_sentence, max_length=100, min_length=min_length)
        
    else:
        summ = ''
        
    return summ