from fuzzywuzzy import fuzz
from src.graph_database import GraphDatabase

graph_db = GraphDatabase()
entity_types = ['Task','Method','Metric','OtherScientificTerm','Abbreviation','Material']

nodes = []

for entity_type in entity_types:
    nodes += graph_db.get_all_entities(entity_type)

# in real case we will have property that collect list of linked_names
# in this case i will use weight insteat of list to simulate

entities_all_name = []
for node in nodes:
    node_name = []
    node_name.append(node.name) #main_name will be first index

    # node_name += node.linked_name #real test
    node_name.append(str(node.weight)) # simulate case

    entities_all_name.append(node_name)


keyword = input().strip()

scores = []
for entity in entities_all_name:
    for i,name in enumerate(entity):
        if i == 0:
            main_name = name
        if ' ' in name:
            scores.append((fuzz.token_sort_ratio(keyword.lower(),name.lower()),name,main_name))
        else:
            scores.append((fuzz.ratio(keyword.lower(),name.lower()),name,main_name))

result = sorted(scores,reverse=True)

#to get the top name and it main name
top_name,top_main_name = (result[0][1],result[0][2])
print(top_name,top_main_name)

# print(sorted(scores,reverse=True)[:10])




