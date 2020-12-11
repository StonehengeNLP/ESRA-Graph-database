import re
from neomodel import Q
from fuzzywuzzy import fuzz
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
def search(keys: list, n=10):
    """return ranked papers from subgraph from those keywords using pagerank"""
    print('Search keys:', keys)
    for key in keys:
        if not gdb.is_node_exist(key):
            return ["Entity does not exist"]
    if not gdb.is_cypher_graph_exist(keys):
        gdb.create_cypher_graph(keys)
    results = gdb.pagerank(keys)
    gdb.delete_cypher_graph(keys)
    print('Found papers:', len(results))
    return results[:n]

def explain(keys: list, paper_title):
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