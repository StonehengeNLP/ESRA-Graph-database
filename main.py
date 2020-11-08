import pickle
from src.graph_database import GraphDatabase

with open('data/pickle/arxiv_cscl_200_cleaned.pickle', 'rb') as f:
    data = pickle.load(f)

graph_database = GraphDatabase()
graph_database.clear_all()

for doc in data:
    entities = doc['entities']
    relations = doc['relations']
    
    for entity_type, entity_name, *arg in entities:
        graph_database.add_entity(entity_type, entity_name)
    