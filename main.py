import json
import pickle
from datetime import datetime
from src.graph_database import GraphDatabase

with open('data/pickle/data_5000_cleaned.pickle', 'rb') as f:
    data = pickle.load(f)
    
with open('data/data_5000_mag.json') as f:
    meta = json.load(f)
    meta = {d['Id']:d for d in meta}

graph_database = GraphDatabase()
graph_database.clear_all()

for doc in data[:1]:
    entities = doc['entities']
    relations = doc['relations']
    id = doc['id']
    print(meta[id])
    
    # metadata adding section
    creation_date = datetime.strptime(meta[id]['D'], '%Y-%m-%d')
    paper_entity = graph_database.add_entity('Paper', meta[id]['DN'], created=creation_date)
    for author in meta[id]['AA']:
        author_entity = graph_database.add_entity('Author', author['DAuN'])
        graph_database.add_relation('Author-of', author_entity, paper_entity)
        if 'AfN' in author:
            affiliation_entity = graph_database.add_entity('Affiliation', author['AfN'])
            graph_database.add_relation('Affiliate-with', author_entity, affiliation_entity)
    
    # information adding section
    entity_cache = []
    for entity_type, entity_name, confidence, *args in entities:
        entity = graph_database.add_entity(entity_type, entity_name, confidence)
        graph_database.add_relation('Appear-in', entity, paper_entity, confidence)
        entity_cache += [entity]
    for relation_type, head, tail, confidence, *args in relations:
        graph_database.add_relation(relation_type, 
                                    entity_cache[head], 
                                    entity_cache[tail],
                                    confidence)