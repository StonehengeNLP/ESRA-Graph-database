import json

with open('data.json') as f:
    data = json.load(f)
    
with open('mapping.json') as f:
    mapping = json.load(f)
    
out = []
for d, m in zip(data, mapping):
    arxiv_id, title, section = m
    if arxiv_id == '1908.10084':
        if not d.endswith('.'):
            d = d + '.'
        out += [d]
        
print(' '.join(out))