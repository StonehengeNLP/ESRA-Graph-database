from src.graph_database import GraphDatabase


gdb = GraphDatabase()

RELATION_TYPE_MAPPING = {
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


# NOTE: new version
def template(keys, paper_title):
    """
    template for generating explanation
    """
    tasks = []
    methods = []
    others = []
    local_graph = gdb.query_local_graph(paper_title)
    for path in local_graph:
        if len(path) == 1: #entity in graph
            entity_name, entity_type = path[0][1]
            if entity_type  == 'Task':
                tasks.append(entity_name)
            elif entity_type == 'Method':
                methods.append(entity_name)
            else:
                others.append(f"{entity_name}({entity_type})")

        #TODO: use local relations to enchance the explanation.  
        if len(path) == 2: #relation in local graph
            pass

    if len(tasks) == 0 and len(methods) > 0:
        explanation = f"This paper using {str(len(methods))} {'methods' if len(methods) > 1 else 'method'} " + \
                      f"which are {', '.join([str(method) for method in methods])}."
    elif len(tasks) > 0 and len(methods) == 0:
        explanation = f"This paper doing {str(len(tasks))} {'tasks' if len(tasks) > 1 else 'task'} " + \
                      f"which are {', '.join([str(task) for task in tasks])}."
    elif len(tasks) > 0 and len(methods) > 0:
        explanation = f"This paper doing {str(len(tasks))} {'tasks' if len(tasks) > 1 else 'task'} " + \
                      f"which are {', '.join([str(task) for task in tasks])} and using {str(len(methods))} {'methods' if len(methods) > 1 else 'method'} " + \
                      f"which are {', '.join([str(method) for method in methods])}."
    else:
        explanation = f"This paper mentioned {', '.join([str(other) for other in others])}."

    return explanation

paper_title = "A Neural Attention Model for Abstractive Sentence Summarization"
keys = []
print(template(keys, paper_title))




# NOTE: old version
# def template(keys, paper_title):
#     paths = gdb.get_paths(keys, paper_title)
    
#     # calculate sum of weight of each path in order to rank
#     ranking = []
#     for i, path in enumerate(paths):
#         weight = 0
#         for relation in path:
#             if relation[0] == 'refer_to':
#                 weight += float('-inf')
#             else:
#                 weight += relation[1]
#         ranking.append([weight,i])

#     # pick n paths that have most weight
#     MAXIMUM_PATH = 2
#     ranking.sort(reverse=True)
#     if MAXIMUM_PATH > len(paths):
#         MAXIMUM_PATH = len(paths)
#     picked_idx = [ranking[i][1] for i in range(MAXIMUM_PATH)]

#     # show explanation
#     out = []
#     for idx in picked_idx:
#         explain_path = paths[idx]
#         explanation = ''
#         for i,relation in enumerate(explain_path):
#             if i == 0:
#                 explanation += relation[2][0] + '(' + relation[2][1][0] + ') ' # start node
            
#             # relation_type_cases
#             explanation += RELATION_TYPE_MAPPING[relation[0]]
            
#             if i != len(explain_path)-1:
#                 explanation += relation[3][0] + '(' + relation[3][1][0] + ') ' # between node
        
#         out += [explanation]
#     return out