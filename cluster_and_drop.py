import re
import tqdm
import string
import neomodel
import requests
import numpy as np
import en_core_web_sm
import json
import torch

from sklearn.cluster import DBSCAN
from sentence_transformers import util
from sentence_transformers import SentenceTransformer

from src import models
from src.graph_database import GraphDatabase
from offline_setup_util import load_sent_trans_model

import nltk
from nltk.stem.porter import *
try:
    # nltk.data.find('corpus/stopwords')
    from nltk.corpus import stopwords
except ImportError:
    nltk.download('stopwords')
    from nltk.corpus import stopwords
stop_words = set(stopwords.words('english')) 

nlp = en_core_web_sm.load()

gdb = GraphDatabase()
stemmer = PorterStemmer()

url = "https://raw.githubusercontent.com/hyperreality/American-British-English-Translator/master/data/american_spellings.json"

try:
    with open('data/american_spelling.json', 'r') as f:
        american_to_british_dict = json.load(f)    
except FileNotFoundError:
    american_to_british_dict = requests.get(url).json()

def britishize(string):
    for american_spelling, british_spelling in american_to_british_dict.items():
        string = string.replace(american_spelling, british_spelling)
    return string

def stem(text):
    text = ' '.join([stemmer.stem(i) for i in text.split()])
    return text

def lemmatize(text):
    doc = nlp(text)
    text = ' '.join([i.lemma_ for i in doc])
    return text

def is_similar(cluster: list):
    if len(cluster) > 2:
        return False

    a = re.sub(r'[^a-zA-Z0-9\s]+', '', cluster[0])
    b = re.sub(r'[^a-zA-Z0-9\s]+', '', cluster[1])
    a = re.sub(r'\s+', ' ', a).strip()    
    b = re.sub(r'\s+', ' ', b).strip()
    aa = re.sub(r'\s+', '', a)    
    bb = re.sub(r'\s+', '', b)  
    if aa.startswith(bb) or bb.startswith(aa):
        return True
    
    a = ' '.join([w for w in a.split() if w not in stop_words])
    b = ' '.join([w for w in b.split() if w not in stop_words])
    if a.startswith(b) or b.startswith(a):
        return True

    a = lemmatize(a)
    b = lemmatize(b)
    if a.startswith(b) or b.startswith(a):
        return True
    
    a = britishize(a)
    b = britishize(b)
    if a.startswith(b) or b.startswith(a):
        return True
    
    a = stem(a)
    b = stem(b)
    if a.startswith(b) or b.startswith(a):
        return True
    
    return False

def merge_cluster(cluster: list, entity_type):
    entity = [gdb.get_entity(entity_type, name=name) for name in cluster]
    entity = sorted(entity, key=lambda x: x.count)
    selected = entity.pop(-1)
    
    # Update nodes parameters
    for e in entity:
        selected.count += e.count
        for k, v in e.variants.items():
            if k in selected.variants:
                selected.variants[k] += v
            else:
                selected.variants[k] = v
        _weight_diff = (e.weight - selected.weight) / selected.count
        selected.weight += _weight_diff
    
        # Update relations
        for relation_type in RELATION_TYPES:

            # Redirect incoming relations
            definition = dict(
                node_class=models.BaseEntity, direction=neomodel.match.INCOMING,
                relation_type=relation_type, model=None,
            )
            relations_traversal = neomodel.match.Traversal(e, 'whatever', definition)
            all_relations = relations_traversal.all()
            
            for node in all_relations:
                relation = gdb.get_relation(relation_type, node)
                old_relationship = relation.relationship(e)
                
                if gdb.is_relation_exist(relation_type, node, selected):
                    new_relationship = relation.relationship(selected)
                    new_relationship.count += old_relationship.count
                    new_relationship.weight += old_relationship.weight
                else:
                    new_relationship = relation.connect(selected)
                    new_relationship.count = old_relationship.count
                    new_relationship.weight = old_relationship.weight
                new_relationship.save()
                
            # Redirect outgoing relations
            selected_relation = gdb.get_relation(relation_type, selected)
            definition = dict(
                node_class=models.BaseEntity, direction=neomodel.match.OUTGOING,
                relation_type=relation_type, model=None,
            )
            relations_traversal = neomodel.match.Traversal(e, 'whatever', definition)
            all_relations = relations_traversal.all()
            
            for node in all_relations:
                relation = gdb.get_relation(relation_type, e)
                old_relationship = relation.relationship(node)
                
                if gdb.is_relation_exist(relation_type, selected, node):
                    new_relationship = selected_relation.relationship(node)
                    new_relationship.count += old_relationship.count
                    new_relationship.weight += old_relationship.weight
                else:
                    new_relationship = relation.connect(node)
                    new_relationship.count = old_relationship.count
                    new_relationship.weight = old_relationship.weight
                new_relationship.save()
        e.delete()
    selected.best_variant = max(selected.variants, key=selected.variants.get)
    selected.save()
    
ENTITY_TYPES = [
    'Task',
    'Method',
    'Material',
    'OtherScientificTerm',
    'Metric',
    'Abbreviation',
]

RELATION_TYPES = [
    'used_for',
    'part_of',
    'feature_of',
    'compare',
    'hyponym_of',
    'evaluate_for',
    'refer_to',
    'related_to',
    'appear_in',
]

# torch device
device = 1 if torch.cuda.is_available() else 'cpu' 
print(f'Use device: {device}')

for entity_type in ENTITY_TYPES:
    data = [i.name for i in gdb.get_all_entities(entity_type)]

    data = sorted(list(set(data)))
    data = np.array(data)
    print(len(data))

    # model = SentenceTransformer('paraphrase-distilroberta-base-v1')
    model = load_sent_trans_model('paraphrase-distilroberta-base-v1', device=device)
    sentence_embeddings = model.encode(data, 64, show_progress_bar=True)

    clustering = DBSCAN(eps=3, min_samples=2, n_jobs=-1).fit(sentence_embeddings)
    arr = clustering.labels_
    
    for i in tqdm.tqdm(range(arr.max())):
        idx = np.where(arr == i)
        d = list(data[idx])
        
        # If they are similar
        if is_similar(d):
            
            # Merge the cluster
            merge_cluster(d, entity_type)
            
    # # NOTE: For testing
    # with open('clustering_dataset.txt') as f:
    #     data = [line.strip().split(', ') for line in f.readlines()]

    # result = {'TRUE': {True: 0, False: 0}, 'FALSE': {True: 0, False: 0}}
    # for line in tqdm.tqdm(data):
    #     true = line[0]
    #     pred = is_similar(line[1:])
    #     result[true][pred] += 1
    #     if pred:
    #         # print(line)
    #         merge_cluster(line[1:], entity_type)
    #     else:
    #         pass
    # print(result)
