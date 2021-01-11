import os
import scipy
import pickle
from functools import lru_cache
from sentence_transformers import SentenceTransformer

# Prepare model
model_roberta = SentenceTransformer('roberta-large-nli-mean-tokens', device='cpu')

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
    print('finished the vocab embeddings ...')
    
with open(vocab_embeddings_path, 'rb') as f:
    vocab_embeddings = pickle.load(f)

@lru_cache(maxsize=128)
def get_related_word(query, threshold=0.9, limit=5):
    """
    Semantic search function
    
    Input:
        query(str): keyword to be searched
    Output:
        dict of keywords and their list of related keywords
    """
    if isinstance(query, str):
        queries = [query]
    elif isinstance(query, list):
        queries = query
        
    query_embeddings = model_roberta.encode(queries)

    out = {}
    
    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], vocab_embeddings, "cosine")[0]

        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        out[query] = []
        for idx, distance in results:
            
            # check threshold and length limit
            if 1 - distance < threshold or len(out[query]) >= limit:
                break
            
            # check query not include in the word
            if query not in vocab[idx]:
                out[query] += [vocab[idx]]
                
    return out