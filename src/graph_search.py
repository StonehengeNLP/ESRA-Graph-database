import re
import numpy as np
from neomodel import Q
from fuzzywuzzy import fuzz
from datetime import datetime
from rank_bm25 import BM25Okapi
from .graph_database import GraphDatabase

RELATION_TYPE_MAPPING = {
    'refer_to': 'also known as ',
    'used_for': 'used for ',
    'evaluate_for' : 'uses to evaluate ',
    'hyponym_of': 'is a ',
    'part_of': 'is a part of ',
    'feature_of': 'is a feature of ',
    'compare': 'usually compare with ',
    'related_to': 'is related to ',
    'appear_in': 'which is appear in this paper.'
}

gdb = GraphDatabase()

def text_autocomplete(text, n=10):
    """suggest top 10 similar keywords based on the given text"""
    base_entity = gdb.get_entity_model('BaseEntity')
    nodes = base_entity.nodes.filter(name__istartswith=text.lower())
    suggested_list = list({node.name.lower() for node in nodes[:100]})
    return sorted(suggested_list, key=len)[:n]

def text_correction(text, limit=1000, length_vary=0.2):
    """correct the text to be matched to a node"""
    text = text.lower()
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

def text_preprocessing(search_text, threshold=90):
    """correct and filter n-gram keywords by similarity threshold"""
    n = len(search_text.split())
    new_keywords = []
    while n:
        keywords = _generate_ngrams(search_text, n=n)
        for keyword in keywords:
            new_word, score = text_correction(keyword, length_vary=0.1)
            if score >= threshold:
                new_keywords += [new_word]
        n -= 1
    new_keywords = _drop_insignificant_words(new_keywords)
    return new_keywords

# TODO: prevent injection
def search(keys: list, n=10, mode='pagerank'):
    """return ranked papers from subgraph from those keywords using pagerank"""
    print('Search keys:', keys)
    if mode == 'pagerank':
        results = _search_pagerank(keys, n)
    elif mode == 'bm25':
        results = _search_bm25(keys, n)
    elif mode == 'popularity':
        results = _search_popularity(keys, n)
    return results
    
def _search_pagerank(keys, n):
    for key in keys:
        if not gdb.is_node_exist(key):
            return ["Entity does not exist"]
    if not gdb.is_cypher_graph_exist(keys):
        gdb.create_cypher_graph(keys)
    results = gdb.pagerank(keys)
    gdb.delete_cypher_graph(keys)
    return results[:n]

def _search_bm25(keys, n):
    papers = gdb.get_all_entities('Paper')
    corpus = [p.abstract.lower() for p in papers]
    tokenized_corpus = [doc.split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    doc_scores = bm25.get_scores(keys)
    ind = np.argpartition(doc_scores, -10)[-n:]
    res_ind = ind[np.argsort(doc_scores[ind])][::-1]
    results = []
    for i in res_ind:
        score = doc_scores[i]
        paper = papers[i]
        results += [[score, paper.cc, paper.name]]
    return results

# NOTE: now this is only title
def _search_popularity(keys, n):
    results = []
    papers = gdb.get_all_entities('Paper')
    for p in papers:
        days = (datetime.now() - p.created).days
        cc = p.cc
        popular = cc / days
        count = 0
        for key in keys:
            if key in p.name.lower():
                count += 1
        results += [[popular * count, p.cc, p.name]]
    results = sorted(results, key=lambda x: x[0])[::-1]
    return results[:n]

def explain(keys: list, paper_title, mode='template'):
    if mode == 'template':
        return _explain_template(keys, paper_title)
    if mode == 'kg2text':
        return _explain_kg2text(keys, paper_title)

def _explain_template(keys, paper_title):
    paths = gdb.get_paths(keys, paper_title)
    
    # calculate sum of weight of each path in order to rank
    ranking = []
    for i, path in enumerate(paths):
        weight = 0
        for relation in path:
            if relation[0] == 'refer_to':
                weight += float('-inf')
            else:
                weight += relation[1]
        ranking.append([weight,i])

    # pick n paths that have most weight
    MAXIMUM_PATH = 2
    ranking.sort(reverse=True)
    if MAXIMUM_PATH > len(paths):
        MAXIMUM_PATH = len(paths)
    picked_idx = [ranking[i][1] for i in range(MAXIMUM_PATH)]

    # show explanation
    out = []
    for idx in picked_idx:
        explain_path = paths[idx]
        explanation = ''
        for i,relation in enumerate(explain_path):
            if i == 0:
                explanation += relation[2][0] + '(' + relation[2][1][0] + ') ' # start node
            
            # relation_type_cases
            explanation += RELATION_TYPE_MAPPING[relation[0]]
            
            if i != len(explain_path)-1:
                explanation += relation[3][0] + '(' + relation[3][1][0] + ') ' # between node
        
        out += [explanation]
    return out
        
def _prepare_kg2text(keys: list, paper_title: str):
        entities = []
        types = []
        relations = []
        paths = gdb.get_paths(keys, paper_title)
        for path in paths:
            for r, w, s, e in path:
                if s[0] not in entities and 'Paper' not in s[1]:
                    entities += [s[0]]
                    t = s[1][0].lower()
                    if t == 'abbreviation':
                        t = 'method'
                    types += [t]
                if e[0] not in entities and 'Paper' not in e[1]:
                    entities += [e[0]]
                    t = e[1][0].lower()
                    if t == 'abbreviation':
                        t = 'method'
                    types += [t]
                if s[0] in entities and e[0] in entities:
                    if r == 'refer_to':
                        r = 'hyponym_of'
                    rel = [s[0], r.upper().replace('_', '-'), e[0]]
                    if rel not in relations:
                        relations += [rel]
        d = {}
        d['title'] = paper_title
        d['entities'] = entities
        d['types'] = ' '.join([f'<{i}>' for i in types])
        d['relations'] = [' -- '.join(rel) for rel in relations]
        d['abstract'] = ' '.join([f'<{t}_{i}>' for i, t in enumerate(types)])
        d['abstract_og'] = ' '.join(entities)
        return d

# TODO: add the model to this system        
def _explain_kg2text(keys: list, paper_title): 
    return _prepare_kg2text(keys, paper_title)
    
    if isinstance(paper_title, str):
        _prepare_kg2text(keys, paper_title)
        
    elif isinstance(paper_title, list):
        for title in paper_title:
            _prepare_kg2text(keys, paper_title)
            