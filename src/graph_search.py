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

gdb = GraphDatabase()

# Prepare data
proj_dir = os.path.dirname(os.path.dirname(__file__))
vocab_path = os.path.join(proj_dir, 'data/vocab.txt')

with open(vocab_path, encoding='utf-8') as f:
    vocab = [i.strip() for i in f.readlines()]
vocab_set = set(vocab)

@lru_cache(maxsize=128)
def text_autocomplete(text, n=10):
    """suggest top 10 similar keywords based on the given text"""
    suggested_list = list(filter(lambda k: k.startswith(text.lower()), vocab))
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
    
    len_min, len_max = int(max(0, len(text) * (1-length_vary))), int(len(text) * (1+length_vary))
    base_entity = gdb.get_entity_model('BaseEntity')
    # filtered by the first or second character
    # and the length is +- length_vary * length? 
    nodes = base_entity.nodes.filter(
        (Q(name__istartswith=text[0]) | Q(name__regex=rf'^.{text[1]}.*')) 
        & Q(name__regex=rf'^.{{{len_min},{len_max}}}$'))
    suggested_list = list({node.name.lower() for node in nodes[:limit]})
    score = lambda x: fuzz.ratio(text, x.lower())
    if suggested_list:
        best = max(suggested_list, key=score)
        # cut-off threshold 
        best_score = score(best)
        if best_score > 60:
            return best, best_score
    return None, 0

def _generate_ngrams(s, n):
    s = s.lower()
    tokens = [token for token in s.split(" ") if token != ""]
    ngrams = zip(*[tokens[i:] for i in range(n)])
    ngrams = [" ".join(ngram) for ngram in ngrams]
    return ngrams

# NOTE: the keywords must be sorted as _generate_ngrams()
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
    
    n = len(search_text.split())
    new_keywords = []
    while n:
        keywords = _generate_ngrams(search_text, n=n)
        for keyword in keywords:
            new_word, score = text_correction(keyword, length_vary=0.05)
            if score >= threshold:
                new_keywords += [new_word]
            else:
                suggest_word = get_related_word(keyword, threshold=0.96, limit=1)[keyword]
                if suggest_word != []:
                    new_keywords += [suggest_word[0]]
        n -= 1
    
    # drop insignificant words
    new_keywords = _drop_insignificant_words(new_keywords)

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
def get_facts(keys: tuple):
    """
    Get facts (relation) with highest confidence from the graph
    Plus, there will be other nodes which are added to show relationship between them
    """
    # facts
    fact_list, scheme = gdb.get_one_hops(keys)
    facts = [{k:v for k, v in zip(scheme, fact)} for fact in fact_list]
    # other relations
    other_relation, scheme = gdb.query_keyword_graph(keys)
    others = [{k:v for k, v in zip(scheme, rel)} for rel in other_relation]
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

# # TODO: prevent injection
# def search(keys: list, n=10, mode='pagerank'):
#     """return ranked papers from subgraph from those keywords using pagerank"""
#     if mode == 'pagerank':
#         results = _search_pagerank(keys, n)
#     elif mode == 'bm25':
#         results = _search_bm25(keys, n)
#     elif mode == 'popularity':
#         results = _search_popularity(keys, n)
#     return results
    
# def _search_pagerank(keys, n):
#     for key in keys:
#         if not gdb.is_node_exist(key):
#             return ["Entity does not exist"]
#     if not gdb.is_cypher_graph_exist(keys):
#         gdb.create_cypher_graph(keys)
#     results = gdb.pagerank(keys)
#     gdb.delete_cypher_graph(keys)
#     return results[:n]

# def _search_bm25(keys, n):
#     papers = gdb.get_all_entities('Paper')
#     corpus = [p.abstract.lower() for p in papers]
#     tokenized_corpus = [doc.split() for doc in corpus]
#     bm25 = BM25Okapi(tokenized_corpus)
#     doc_scores = bm25.get_scores(keys)
#     ind = np.argpartition(doc_scores, -10)[-n:]
#     res_ind = ind[np.argsort(doc_scores[ind])][::-1]
#     results = []
#     for i in res_ind:
#         score = doc_scores[i]
#         paper = papers[i]
#         results += [[score, paper.cc, paper.name]]
#     return results

# # NOTE: now this is only title
# def _search_popularity(keys, n):
#     results = []
#     papers = gdb.get_all_entities('Paper')
#     for p in papers:
#         days = (datetime.now() - p.created).days
#         cc = p.cc
#         popular = cc / days
#         count = 0
#         for key in keys:
#             if key in p.name.lower() or key in p.abstract.lower():
#                 count += 1
#         results += [[popular * count, p.cc, p.name]]
#     results = sorted(results, key=lambda x: x[0])[::-1]
#     return results[:n]