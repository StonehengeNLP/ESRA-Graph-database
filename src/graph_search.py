import os
import re
import numpy as np
from neomodel import Q
from fuzzywuzzy import fuzz
from datetime import datetime
from functools import lru_cache
from rank_bm25 import BM25Okapi
from .graph_database import GraphDatabase
from .semantic_search import get_related_word

import nltk
try:
    nltk.data.find('corpus/stopwords')
except LookupError:
    nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))  

gdb = GraphDatabase()

# Prepare data
proj_dir = os.path.dirname(os.path.dirname(__file__))
vocab_path = os.path.join(proj_dir, 'data/vocab.txt')
full_vocab_path = os.path.join(proj_dir, 'data/full_vocab.txt')

with open(vocab_path, encoding='utf-8') as f:
    vocab = [i.strip() for i in f.readlines()]
vocab_set = set(vocab)

with open(full_vocab_path, encoding='utf-8') as f:
    full_vocab = [i.strip() for i in f.readlines()]
full_vocab_set = set(full_vocab)

@lru_cache(maxsize=128)
def text_autocomplete(text, n=10):
    """suggest top 10 similar keywords based on the given text"""
    suggested_list = list(set(filter(lambda k: k.startswith(text.lower()), vocab)))
    return sorted(suggested_list, key=len)[:n]

@lru_cache(maxsize=128)
def text_correction(text, limit=1000, length_vary=0.2):
    """
    correct the text to be matched to a node
    if it is already in the vocab set, return it immediately
    """
    text = text.lower()
    
    if text in vocab_set:
        return text, 100
    
    score = lambda x: fuzz.ratio(text, x.lower())
    
    # Filter before calculation -> can improve speed
    selected_vocab = [word for word in vocab if bool(set(word[:2]) & set(text[:2]))]
    best = max(selected_vocab, key=score)
    
    # cut-off threshold 
    best_score = score(best)
    if best_score > 60:
        return best, best_score
    return None, 0

def _drop_insignificant_words(keywords: list):
    """remove unpopular words which are subtext and less number than another one"""
    d = {}
    for keyword in keywords:
        c = gdb.count_entity(keyword)
        for k in d:
            if keyword in k and c < d[k]:
                break
        else:
            d[keyword] = c
    return list(d.keys())

@lru_cache(maxsize=128)
def text_preprocessing(search_text, threshold=95, flatten=False, expand=True):
    """correct and filter n-gram keywords by similarity threshold"""
    search_text = search_text.lower()
    
    # Check exact match
    if search_text in full_vocab_set:
        new_keywords = [search_text]
    
    # Non exact match
    else:
        search_text_list = search_text.split()
        
        i = 0
        new_keywords = []
        while i < len(search_text_list):
            n = min(3, len(search_text_list) - 1)
            while n:
                keyword = ' '.join(search_text_list[i:i+n])

                if keyword in stop_words:
                    i += 1
                    continue
                new_word, score = text_correction(keyword, length_vary=0.05)

                if score >= threshold:
                    new_keywords += [new_word]
                    ############################################
                    # FOR fixing the `medical nlp` case 
                    ############################################
                    i += n
                    break
                    ############################################
                else:
                    suggest_word = get_related_word(keyword, threshold=0.9, limit=1)[keyword]

                    if suggest_word != [] and keyword not in suggest_word[0]:
                        new_keywords += [suggest_word[0]]
                n -= 1
            else:
                i += 1
    
    # # drop insignificant words
    # new_keywords = _drop_insignificant_words(new_keywords)

    # find other relavant words
    if expand:
        new_keywords = get_related_word(tuple(new_keywords))
    
        # flatten the keywords in dict format
        if flatten:
            flatten_list = []
            for k, v in new_keywords.items():
                flatten_list += [k] + v
            return flatten_list

    return new_keywords

@lru_cache(maxsize=32)
def get_facts(keys: tuple, limit: int):
    """
    Get facts (relation) with highest confidence from the graph
    Plus, there will be other nodes which are added to show relationship between them
    """
    # facts
    fact_list, scheme = gdb.get_one_hops(keys, limit)
    facts = [{k:v for k, v in zip(scheme, fact)} for fact in fact_list]
    facts_without_paper = [[v for k, v in fact.items() if k not in ['papers', 'score']] for fact in facts]
    
    # other relations
    other_relation, scheme = gdb.query_keyword_graph(keys)
    others = [{k:v for k, v in zip(scheme, rel)} for rel in other_relation if rel not in facts_without_paper]
    return facts, others

@lru_cache(maxsize=128)
def query_graph(paper_title, limit):
    """
    This function is for visualization in frontend using D3.js
    just a proxy of gdb.query_graph
    """
    return gdb.query_graph(paper_title, limit)

@lru_cache(maxsize=128)
def query_graph_key_paper(keys, paper_title, limit):
    """
    Proxy function for gdb.query_graph_key_paper. Uses for query graph
    containing path from kwyword to paper.
    """
    return gdb.query_graph_key_paper(keys, paper_title, limit)
