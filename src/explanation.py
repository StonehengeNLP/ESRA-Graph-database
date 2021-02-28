import nltk
from nltk.tokenize import sent_tokenize 

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
  
import re
import spacy
import torch
import pandas as pd
import concurrent.futures
from functools import lru_cache
from collections import defaultdict
from .graph_database import GraphDatabase
from .multipipeline import MultiPipeline
    
import logging
logger = logging.getLogger("spacy")
logger.setLevel(logging.ERROR)

gdb = GraphDatabase()

t5_small = MultiPipeline()
nlp = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'ner'])

# # Open arxiv-to-summary file and convert it into dict
# id_to_summary = pd.read_csv('data/csv/kaggle-arxiv-cscl-2020-12-18-with_summary.csv')
# id_to_summary = id_to_summary.set_index('id')[['summary']].to_dict()['summary']

def lemmatize(text, lem_to_kw=False):
    doc = nlp(text.lower())
    lem_list = ' '.join([w.lemma_ for w in doc])
    if lem_to_kw:
        lem_map = defaultdict(set)
        for w in doc:
            lem_map[w.lemma_].add(w.orth_)
        return lem_list, lem_map
    return lem_list
    
def is_include_word(word, text):
    """ 
    return true if the word is included in the text
    
    you could make it smarter :D
    """
    r = re.search(rf'\b{re.escape(word)}\b', text, re.IGNORECASE)
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
def _summarize(sentence, max_length=100, min_length=50):
    """
    this function is for summarizing sentences
    """
    word_count = count_word(sentence)

    if word_count < 50:
        return sentence
    else:
        min_length = min(min_length, word_count)
        max_length = min(max_length, word_count)
        summ = t5_small(sentence, max_length=max_length, min_length=min_length)[0]['summary_text']
        summ = beautify(summ)
        return summ

def _filter_sentences(keywords: list, abstract: str) -> str:
    """
    Filter some sentences from abstract by given keywords
    then summarize
    """
    sentences = sent_tokenize(abstract)
    
    selected_sentence = []
    for sentence in sentences:
        lem_sent = lemmatize(sentence)
        n = 0
        for name in keywords:
            if is_include_word(name, lem_sent):
                selected_sentence += [sentence]
                n += 1
            if n == 2:
                break
            
    new_sentence = ' '.join(selected_sentence)
    return new_sentence
        
def filtered_summarization(keyword:str, processed_keys:list, title:str, abstract:str) -> list:
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
        
    # Get all related keywords from graph
    all_key_nodes = {keyword} | set(processed_keys)
    nodes = gdb.get_related_nodes(tuple(all_key_nodes), title)
    lem_all_keys = [lemmatize(k) for k in all_key_nodes]
    
    # Get all sentences related to keywords
    filter_words = list(nodes) + list(all_key_nodes)
    lem_filter_words = [lemmatize(k) for k in filter_words]
    filtered_text = _filter_sentences(lem_filter_words, abstract)
    
    # print(filtered_text)
    # print(count_word(filtered_text))
    
    # Also get keywords from title
    lem_title, lem_map_title = lemmatize(title, lem_to_kw=True)
    
    # Put the sentences into summarizer
    summary = _summarize(filtered_text)
    lem_summary, lem_map_summary = lemmatize(summary, lem_to_kw=True)
    keyword_contained = [key for key in lem_all_keys if is_include_word(key, lem_summary + lem_title)]
    
    # When summary does not contain search keys
    if len(keyword_contained) == 0:
        filter_words = filter_words + ['we', 'our', 'in this paper']
        filtered_text = _filter_sentences(filter_words, abstract)
        summary = _summarize(filtered_text)
        lem_summary, lem_map_summary = lemmatize(summary, lem_to_kw=True)
        keyword_contained = [key for key in lem_all_keys if is_include_word(key, lem_summary)]
    
    ###############################
    # # When summary is empty
    # if summary == '':
    #     id_to_summary[]
    ###############################
    
    # Convert the lematized keyword to be original one
    lem_keyword, lem_map_keyword = lemmatize(keyword, lem_to_kw=True)
    lem_map = {**lem_map_keyword, **lem_map_title, **lem_map_summary}
    keyword_contained = [w for key in keyword_contained for word in key.split() for w in lem_map[word]]
    lem_abstract, lem_map_abstract = lemmatize(abstract, lem_to_kw=True)
    keyword_contained_in_abstract = [w for key in lem_all_keys if key not in keyword_contained and is_include_word(key, lem_abstract) for w in lem_map_abstract[key]]
    
    # print(summary)
    # print(keyword_contained)
    # print('*' * 100)
    
    return summary, keyword_contained + keyword_contained_in_abstract
    
    # out += [{'summary': summary, 
    #          'summary_keywords': keyword_contained, 
    #          'abstract_keywords': keyword_contained_in_abstract}]
    
    # return out
