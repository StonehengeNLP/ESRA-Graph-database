import re
import json
import tqdm
import pickle
import pandas as pd
from datetime import datetime
from src.graph_database import GraphDatabase

# Extracted information from entire cs.CL
with open('data/pickle/kaggle_arxiv_cleaned.pickle', 'rb') as f:
    data = pickle.load(f)
    
# Scraped citation and references
with open('data/pickle/kaggle_arxiv_cite_ref.pickle', 'rb') as f:
    cite_ref = pickle.load(f)['data']
    cite_ref = {d['arxiv_id']:d for d in cite_ref}

def clean(title):
    title = re.sub(r'\s+', ' ', title)
    return title

# Arxiv cs.CL dataset
df = pd.read_csv('data/csv/kaggle-arxiv-cscl-2020-12-18.csv')
df.title = df.title.apply(clean)


graph_database = GraphDatabase()
graph_database.clear_all()

for i, doc in tqdm.tqdm(enumerate(data)):
    entities = doc['entities']
    relations = doc['relations']
    arxiv_id = doc['id']
    
    df_row = df[df.id == arxiv_id].iloc[0]
    
    # metadata adding section
    # creation_date = datetime.strptime(meta[mag_id]['D'], '%Y-%m-%d')
    paper_entity = graph_database.add_entity('Paper', 
                                             df_row.title,
                                             paper_id=i,
                                             arxiv_id=arxiv_id,
                                            #  created=creation_date,
                                            #  abstract=meta[mag_id]['ABS'].lower(),
                                            #  cc=meta[mag_id]['CC']
                                             )
    for author in eval(df_row.authors_parsed):
        author_entity = graph_database.add_entity('Author', ' '.join(author))
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
                                    confidence,
                                    from_paper=i)

# add citation relation at the end
for arxiv_id in tqdm.tqdm(cite_ref):
    
    # Check base paper
    if graph_database.is_entity_exist('Paper', arxiv_id=arxiv_id):
        paper = graph_database.get_entity('Paper', arxiv_id=arxiv_id)
        
        # Check reference paper and add relation
        for ref_arxiv_id in cite_ref[arxiv_id]['references']:
            if graph_database.is_entity_exist('Paper', arxiv_id=ref_arxiv_id):
                r_paper = graph_database.get_entity('Paper', arxiv_id=ref_arxiv_id)
                graph_database.add_relation('cite', paper, r_paper)