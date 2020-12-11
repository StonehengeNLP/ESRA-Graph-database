from src.graph_database import GraphDatabase

gdb = GraphDatabase()

results = gdb.find_path(['BERT'],'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding')

relation_type_mapping = {
    'refer_to': 'also known as ',
    'used_for': 'used for ',
    'evaluate_for' : 'uses to evaluate ',
    'hyponym_of': 'is a ',
    'part_of': 'is a part of ',
    'feature_of': 'is a feature of ',
    'compare': 'usually compare with ',
    'related_to': 'is related to ',
    'appear_in': 'which is appear in this paper.'
}

# calculate sum of weight of each path in order to rank
ranking = []
for i,path in enumerate(results):
    weight = 0
    for relation in path:
        if relation[0] == 'refer_to':
            weight += float('-inf')
        else:
            weight += relation[1]
    ranking.append([weight,i])

# pick n paths that have most weight
MAXIMUM_PATH = 2
ranking.sort(reverse=True)
if MAXIMUM_PATH > len(results):
    MAXIMUM_PATH = len(results)
picked_idx = [ranking[i][1] for i in range(MAXIMUM_PATH)]

# show explanation
for idx in picked_idx:
    explain_path = results[idx]
    explanation = ''
    for i,relation in enumerate(explain_path):
        if i == 0:
            explanation += relation[2][0] + '(' + relation[2][1][0] + ') ' #start node
        
        # relation_type_cases
        explanation += relation_type_mapping[relation[0]]
        
        if i != len(explain_path)-1:
            explanation += relation[3][0] + '(' + relation[3][1][0] + ') ' #between node
    
    print(explanation)

