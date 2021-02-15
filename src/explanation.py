import nltk
from nltk.tokenize import sent_tokenize 

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
  
import re
import time
import torch
from functools import lru_cache
from transformers import pipeline
from .graph_database import GraphDatabase

class MultiPipeline:
    
    def __init__(self, num_pipes=1):
        self.pipelines = [pipeline("summarization", model='t5-small', device=i) for i in range(num_pipes)]
        self.locks = [0] * num_pipes
        self.num_pipes = num_pipes
        
    def __call__(self, *args, **kwargs):
        for i in range(self.num_pipes):
            if self.locks[i] == 0:
                self.locks[i] = 1
                result = self.pipelines[i](*args, **kwargs)
                self.locks[i] = 0
                return result
    
gdb = GraphDatabase()

if torch.cuda.is_available():
    t5_small = MultiPipeline(num_pipes=torch.cuda.device_count())
else:
    t5_small = pipeline("summarization", model='t5-small', device='cpu')


def is_include_word(word, text):
    """ 
    return true if the word is included in the text
    
    I have handled plural cases by adding just 's' and 'es'
    you could make it smarter :D
    """
    r = re.search(r'\b{}(s|es){{0,1}}\b'.format(word), text.lower())
    return bool(r)

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
    t = time.time()
    summ = t5_small(sentence, max_length=150, min_length=min_length)[0]['summary_text']
    summ = beautify(summ)
    sum_time = time.time() - t
    print(f'Summarized: {sum_time:.03f}')
    return summ

def _filter_and_summarize(keywords: list, abstract: str) -> str:
    """
    Filter some sentences from abstract by given keywords
    then summarize
    """
    sentences = sent_tokenize(abstract)
    
    selected_sentence = []
    for sentence in sentences:
        n = 0
        for name in keywords:
            if is_include_word(name, sentence):
                selected_sentence += [sentence]
                n += 1
            if n == 4:
                break
            
    new_sentence = ' '.join(selected_sentence)
    word_count = count_word(new_sentence)
    # print(new_sentence)

    if word_count > 10:
        min_length = min(50, word_count)
        summ = _summarize(new_sentence, max_length=100, min_length=min_length)
    else:
        summ = ''
    return summ
        
import time
def filtered_summarization(keyword, processed_keys, title, abstract):
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
    
    # Select a candicate word for each key that is in the given abstract 
    flatten_key = {keyword}
    for key in processed_keys:
        if is_include_word(key, abstract):
            flatten_key.add(key)
        else:
            for related_word in processed_keys[key]:
                if is_include_word(related_word, abstract):
                    flatten_key.add(related_word)
                    break
    flatten_key = list(flatten_key)            
    
    # Get all related keyword. Then filter and summarize
    
    t = time.time()
    nodes = gdb.get_related_nodes(tuple(flatten_key), title)
    
    ##############################
    total = time.time() - t
    print('nodes', len(nodes))
    print(nodes)
    print('total', total)
    ##############################
    
    filter_words = nodes + flatten_key + ['we', 'our', 'in this paper']
    summ = _filter_and_summarize(filter_words, abstract)
    
    # When summary does not contain search keys
    keyword_contained = [key for key in flatten_key if is_include_word(key, summ)]
    if len(keyword_contained) == 0:
        filter_words = flatten_key + ['we', 'our', 'in this paper']
        summ = _filter_and_summarize(filter_words, abstract)
        keyword_contained = [key for key in flatten_key if is_include_word(key, summ)]
        
    return summ, keyword_contained
