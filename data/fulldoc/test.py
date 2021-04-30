import json

with open('data.json') as f:
    data = json.load(f)
    
with open('mapping.json') as f:
    mapping = json.load(f)
    
out = []
for d, m in zip(data, mapping):
    arxiv_id, title, section = m
    if arxiv_id == '1810.04805':
        out += [d]
        
print(' '.join(out))