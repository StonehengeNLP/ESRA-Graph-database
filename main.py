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

for doc in data[:10]:
    entities = doc['entities']
    relations = doc['relations']
    id = doc['id']
    print(meta[id])
    
    # metadata adding section
    creation_date = datetime.strptime(meta[id]['D'], '%Y-%m-%d')
    paper_entity = graph_database.add_entity('Paper', meta[id]['DN'], 
                                             created=creation_date,
                                             mag_id=id,
                                             cc=meta[id]['CC'])
    for author in meta[id]['AA']:
        author_entity = graph_database.add_entity('Author', author['DAuN'])
        graph_database.add_relation('Author-of', author_entity, paper_entity)
        if 'AfN' in author:
            affiliation_entity = graph_database.add_entity('Affiliation', author['AfN'])
            graph_database.add_relation('Affiliate-with', author_entity, affiliation_entity)
    
    # TODO: cite to paper entities in meta[id][RId]
    
    # information adding section
    entity_cache = []
    for entity_type, entity_name, confidence, *args in entities:
        entity = graph_database.add_entity(entity_type, entity_name, confidence)
        graph_database.add_relation('Appear-in', entity, paper_entity, confidence)
        entity_cache += [entity]
    for relation_type, head, tail, confidence, *args in relations:
        try:
            graph_database.add_relation(relation_type, 
                                        entity_cache[head], 
                                        entity_cache[tail],
                                        confidence)
        except Exception as e:
            print(e)