import pickle
from src.graph_database import GraphDatabase

with open('data/pickle/arxiv_cscl_200_cleaned.pickle', 'rb') as f:
    data = pickle.load(f)

graph_database = GraphDatabase()
graph_database.clear_all()

for doc in data:
    entities = doc['entities']
    relations = doc['relations']
    
    entity_cache = []
    for entity_type, entity_name, confidence, *args in entities:
        entity = graph_database.add_entity(entity_type, entity_name, confidence)
        entity_cache += [entity]
        
    for relation_type, head, tail, confidence, *args in relations:
        graph_database.add_relation(relation_type, 
                                    entity_cache[head], 
                                    entity_cache[tail],
                                    confidence)