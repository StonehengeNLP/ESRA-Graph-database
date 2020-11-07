import pickle
from graph_database import GraphDatabase

with open('arxiv_cscl_200_cleaned.pickle', 'rb') as f:
    data = pickle.load(f)

for doc in data:
    entities = doc['entities']
    relations = doc['relations']
    
    for entity in entities:
        print(entity)