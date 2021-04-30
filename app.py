import re
import json
import torch
import concurrent.futures

from src import utils
from src import settings
from src import graph_search as gs
from src import explanation as ex
from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/swagger'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "ESRA GDBM Swagger"
    },
)
app.register_blueprint(swaggerui_blueprint)

@app.route('/swagger')
def swagger():
    with open('swagger.json') as f:
        swagger_json = json.load(f)
        
    swagger_env = settings.FLASK_ENV
    if swagger_env == 'production':
        swagger_json['host'] = 'kpac66ub1.asuscomm.com:58880'
        swagger_json['schemes'] = ['http']

    return swagger_json
    
@app.route('/complete')
def complete():
    query = request.args.get('q')
    if not query:
        return jsonify({'msg': 'Missing query parameter'}), 400
    
    if len(query.strip()) == 0:
        return {'sentences': []}, 200
    
    tokenized_text = query.split()
    for i in range(len(tokenized_text)):
        temp_text = ' '.join(tokenized_text[i:])
        try:
            out = gs.text_autocomplete(temp_text)
        except:
            return jsonify({'msg': 'Database is not available'}), 503
        if out:
            out = [' '.join(tokenized_text[:i] + word.split()) for word in out]
            break
    return jsonify({'sentences': out}), 200

@app.route('/preprocess', methods=['POST'])
def preprocess():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400    
    
    text = request.json.get('text')
    if not text:
        return jsonify({"msg": "Missing 'text' parameter"}), 400
    
    try:
        processed_keywords = gs.text_preprocessing(text)
    except:
        return jsonify({'msg': 'Database is not available'}), 503
    return jsonify(processed_keywords), 200

# NOTE: this may be changed from whole paper titles to just their ids
@app.route('/explain', methods=['POST'])
def explanation():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400    
    
    keyword = request.json.get('keyword')
    papers = request.json.get('papers')
    abstracts = request.json.get('abstracts')
    if not keyword:
        return jsonify({"msg": "Missing 'keyword' parameter"}), 400
    if not papers:
        return jsonify({"msg": "Missing 'papers' parameter"}), 400
    if not abstracts:
        return jsonify({"msg": "Missing 'abstracts' parameter"}), 400
    
    try:
        processed_keywords = gs.text_preprocessing(keyword, flatten=True)
    except Exception as e:
        print(e)
        return jsonify({'msg': 'Database is not available'}), 503
    print('>', processed_keywords)
    num_gpus = max(1, torch.cuda.device_count())
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_gpus) as executor:
        futures = []
        for paper, abstract in zip(papers, abstracts):
            args = (keyword, processed_keywords, paper.lower(), abstract)
            futures += [executor.submit(ex.filtered_summarization, *args)]

    explanations = [r.result(timeout=10) for r in futures]
        
    return jsonify({'explanations': explanations}), 200

import pandas as pd
df = pd.read_csv('data/csv/kaggle-arxiv-cscl-2020-12-18.csv')
id_2_arxiv = df.id.to_dict()

df.title = df.title.apply(lambda t: re.sub(r'\s+', ' ', t))
arxiv_2_title = df.set_index('id')['title'].to_dict()

@app.route('/facts')
def list_of_facts():
    query = request.args.get('q')
    if not query:
        return jsonify({'msg': 'Missing query parameter'}), 400
    
    if len(query.strip()) == 0:
        return {'facts': []}, 200
    
    try:
        processed_keywords = gs.text_preprocessing(query, expand=False, flatten=True)
    except:
        return jsonify({'msg': 'Database is not available'}), 503
    
    fact_list, others = gs.get_facts(tuple(processed_keywords))
    
    #############################
    try:
        for fact in fact_list:
            fact['papers'] = [id_2_arxiv[pid] for pid in fact['papers']]
        for fact in others:
            fact['papers'] = [id_2_arxiv[pid] for pid in fact['papers']]
    except:
        pass
    #############################
    
    # Filter
    get_hashable_object = lambda x: (x['key'], x['name'], x['type'], x['m_labels'][1], x['n_labels'][1], len(x['papers']))
    fact_list_hash = set(get_hashable_object(a) for a in fact_list)
    others = [a for a in others if get_hashable_object(a) not in fact_list_hash]
    
    #############################
    # Temporary post processing
    # 1. merge similar string 2 chars distance for > 10 keyword length
    # 2. combine nodes with the same name but different types
    #############################
    LENGTH = 10
    all_facts = fact_list + others
    for fact_1 in all_facts:
        if len(fact_1['name']) < LENGTH:
            continue
        key_1 = fact_1['name']
        for fact_2 in all_facts:
            if len(fact_2['name']) < LENGTH:
                continue
            key_2 = fact_2['name']
            lcs = utils.LCSubStr(key_1.lower(), key_2.lower())
            
            selected = key_1 if fact_1['m_count'] > fact_2['m_count'] else key_2
            if lcs >= max(len(key_1), len(key_2)) - 2:
                 fact_1['name'] = selected
                 fact_2['name'] = selected
    
    # Combine same name nodes of keys
    max_key_count_type = sorted([(fact['key'], fact['n_count'], fact['n_labels'][1]) for fact in all_facts], reverse=True)
    
    prev_key = -1
    for this_fact, this_count, this_label in max_key_count_type:
        
        if prev_key == this_fact:
            continue
        
        for fact_2 in all_facts:
            key_2 = fact_2['key']
            count_2 = fact_2['n_count']
            
            if this_fact.lower() == key_2.lower() and this_count > 2 * count_2:
                fact_2['n_labels'][1] = this_label
                
        prev_key = this_fact
        
    # Combine same name nodes of other nodes
    max_key_count_type = sorted([(fact['name'], fact['m_count'], fact['m_labels'][1]) for fact in all_facts], reverse=True)
    
    prev_key = -1
    for this_fact, this_count, this_label in max_key_count_type:
        
        if prev_key == this_fact:
            continue
        
        for fact_2 in all_facts:
            key_2 = fact_2['name']
            count_2 = fact_2['m_count']
            
            if this_fact.lower() == key_2.lower() and this_count > 2 * count_2:
                fact_2['m_labels'][1] = this_label
                
        prev_key = this_fact
    
    def is_violate_refer_to(key, abbrv):
        i = j = 0
        key = key.lower()
        abbrv = abbrv.lower()
        while i < len(abbrv):
            if abbrv[i] == key[j]:
                i += 1
                j += 1
            elif abbrv[i] == '2':
                i += 1
            else:
                j += 1
            if j >= len(key):
                return True
        return False
    
    # Merge duplicate relations again
    get_hashable_object = lambda x: (x['key'], x['name'], x['type'], x['m_labels'][1], x['n_labels'][1])
    out = {}
    for fact in fact_list:
        key = get_hashable_object(fact)
        if key not in out:
            # Check not violate refer_to
            if key[2] == 'refer_to':
                if len(key[0]) < len(key[1]):
                    if is_violate_refer_to(key[1], key[0]):
                        continue
                else:
                    if is_violate_refer_to(key[0], key[1]):
                        continue
                    
            out[key] = fact
        out[key]['papers'] += [arxiv_id for arxiv_id in fact['papers'] if arxiv_id not in out[key]['papers']]
    #############################
    
    # Conver paper to arxiv ids
    return {'facts': list(out.values())[:15], 'others': []}, 200

@app.route('/graph')
def graph():
    arxiv_id = request.args.get('arxiv_id')
    limit = request.args.get('limit', 30, type=int)
    
    paper_title = arxiv_2_title.get(arxiv_id, None)
    
    if not paper_title:
        return jsonify({"msg": "Missing 'arxiv_id' parameter"}), 400
    
    graph = gs.query_graph(paper_title=paper_title, limit=limit)
    return {'graph': graph}, 200

@app.route('/kwGraph')
def kwGraph():
    keys = request.args.get('keys')
    arxiv_id = request.args.get('arxiv_id')
    limit = request.args.get('limit', 30, type=int)

    paper_title = arxiv_2_title.get(arxiv_id, None)

    if not keys:
        return jsonify({"msg": "Missing 'keys' parameter"}), 400
    if not paper_title:
        jsonify({"msg": "Missing 'arxiv_id' parameter"}), 400

    try:
        processed_keywords = gs.text_preprocessing(keys, flatten=True)
    except:
        return jsonify({'msg': 'Database is not available'}), 503
        
    kwGraph = gs.query_graph_key_paper(keys=tuple(processed_keywords), paper_title=paper_title, limit=limit)
    return {'graph': kwGraph}, 200


if __name__ == '__main__':
    # app.run(debug=False)
    app.run(debug=False, port=8000, host='0.0.0.0') 
