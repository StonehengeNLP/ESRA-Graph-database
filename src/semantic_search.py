import os
import torch
import pickle

from functools import lru_cache
from sentence_transformers import SentenceTransformer, util

# Prepare model
device = 1 if torch.cuda.is_available() else 'cpu'
model_roberta = SentenceTransformer('roberta-large-nli-mean-tokens', device=device)

# Prepare data
proj_dir = os.path.dirname(os.path.dirname(__file__))
vocab_path = os.path.join(proj_dir, 'data/vocab.txt')
vocab_embeddings_path = os.path.join(proj_dir, 'data/vocab_embeddings.pickle')

with open(vocab_path, encoding='utf-8') as f:
    vocab = [i.strip() for i in f.readlines()]
    
if os.path.isfile(vocab_path) and not os.path.isfile(vocab_embeddings_path):
    
    print('building the vocab embeddings ...')
    vocab_embeddings = model_roberta.encode(vocab)
    with open(vocab_embeddings_path, 'wb') as f:
        pickle.dump(vocab_embeddings, f)
    with open(vocab_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(vocab))
    print('finished the vocab embeddings ...')
    
with open(vocab_embeddings_path, 'rb') as f:
    vocab_embeddings = pickle.load(f)

@lru_cache(maxsize=128)
def get_related_word(query, threshold=0.93, limit=3):
    """
    Semantic search function
    
    Input:
        query(str): keyword to be searched
    Output:
        dict of keywords and their list of related keywords
    """

    if isinstance(query, str):
        queries = (query,)
    elif isinstance(query, tuple):
        queries = query
        
    query_embeddings = model_roberta.encode(queries)

    out = {}
    
    for query, query_embedding in zip(queries, query_embeddings):

        cos_scores = util.pytorch_cos_sim(query_embedding, vocab_embeddings)[0]
        scores, indexes = torch.topk(cos_scores, k=limit)
        
        out[query] = []
        for score, idx in zip(scores, indexes):
            
            # check threshold and length limit
            if float(score) < threshold or len(out[query]) >= limit:
                break
            
            # check query not include in the word
            if query not in vocab[idx]:
                out[query] += [vocab[idx]]

    return out
