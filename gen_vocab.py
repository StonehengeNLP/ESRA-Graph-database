import re
from src.graph_database import GraphDatabase
from collections import defaultdict

graph_database = GraphDatabase()
x = graph_database.get_all_entities('BaseEntity')

print(len(x))

def clean_punc(word):
    word = re.sub(r'\"', '', word)
    word = re.sub(r'\\\'', '\'', word)
    word = re.sub(r'^\-', '', word)
    word = re.sub(r'\-$', '', word)
    word = re.sub(r' \- ', '-', word)
    return word

def group_words(words):
    d = defaultdict(int)
    for name, count in words:
        d[name] += count
    return [name for name, count in d.items() if count > 1]

words = [(clean_punc(p.name), p.count) for p in x]
names = group_words(words)

print(len(names))

with open('data/vocab.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(names))
