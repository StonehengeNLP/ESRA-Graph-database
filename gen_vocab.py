from src.graph_database import GraphDatabase

graph_database = GraphDatabase()
x = graph_database.get_all_entities('BaseEntity')

print(len(x))
with open('data/vocab.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join([p.name for p in x[:1000]]))
