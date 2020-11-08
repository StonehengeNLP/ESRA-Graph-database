import pickle
import pandas as pd
from src.graph_database import GraphDatabase

with open('data/pickle/arxiv_cscl_200_cleaned.pickle', 'rb') as f:
    data = pickle.load(f)

df = pd.read_csv('data/csv/arxiv_cscl_200.csv')
df['created'] = df.versions.apply(lambda x: eval(x)[-1]['created'])
df['created'] = pd.to_datetime(df.created)
df['authors_parsed'] = df.authors_parsed.apply(lambda x: [' '.join(author).strip() for author in eval(x)])
df['categories'] = df.categories.str.split()
df = df[['id', 'title', 'authors_parsed', 'categories', 'created']]
meta_data = df.set_index('id').transpose().to_dict()
# print(meta_data)

graph_database = GraphDatabase()
graph_database.clear_all()

for doc in data:
    entities = doc['entities']
    relations = doc['relations']
    id = doc['id']
    
    # metadata adding section
    paper_entity = graph_database.add_entity('Paper', meta_data[id]['title'], created=meta_data[id]['created'])
    for author in meta_data[id]['authors_parsed']:
        author_entity = graph_database.add_entity('Author', author)
        graph_database.add_relation('Author-of', author_entity, paper_entity)
    for category in meta_data[id]['categories']:
        category_entity = graph_database.add_entity('Category', category)
        graph_database.add_relation('In-category', paper_entity, category_entity)
    
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