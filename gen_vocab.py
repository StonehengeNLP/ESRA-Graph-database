import re
from src.graph_database import GraphDatabase
from collections import defaultdict
import string

graph_database = GraphDatabase()

x = []
x += graph_database.get_all_entities('Generic')
x += graph_database.get_all_entities('Task')
x += graph_database.get_all_entities('Method')
x += graph_database.get_all_entities('Material')
x += graph_database.get_all_entities('OtherScientificTerm')
x += graph_database.get_all_entities('Metric')
x += graph_database.get_all_entities('Abbreviation')

print(len(x))

def clean_punc(word):
    # word = re.sub(r'\"', '', word)
    # word = re.sub(r'\\\'', '\'', word)
    # word = re.sub(r'^\-', '', word)
    # word = re.sub(r'\-$', '', word)
    # word = re.sub(r' \- ', '-', word)
    return word.strip(string.punctuation).strip()

def group_words(words):
    d = defaultdict(int)
    for name, count in words:
        d[name] += count
    return [name for name, count in d.items() if count > 0]

words = [(clean_punc(p.name), p.count) for p in x if len(p.name) > 1]

# print('full', len(words))
# with open('data/full_vocab.txt', 'w', encoding='utf-8') as f:
#     f.write('\n'.join(list(set([w for w, c in words]))))

names = group_words(words)
names = sorted(list(set(names)))

print(len(names))

with open('data/vocab_for_dedup.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(names))
