import torch
import json
import concurrent.futures

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
        swagger_json['host'] = '13.250.112.78:58880'
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
        processed_keywords = gs.text_preprocessing(keyword)
    except Exception as e:
        print(e)
        return jsonify({'msg': 'Database is not available'}), 503
    
    num_gpus = torch.cuda.device_count()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_gpus) as executor:
        futures = []
        for paper, abstract in zip(papers, abstracts):
            args = (keyword, processed_keywords, paper.lower(), abstract)
            futures += [executor.submit(ex.filtered_summarization, *args)]

    explanations = [r.result() for r in futures]
        
    return jsonify({'explanations': explanations}), 200

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
    return {'facts': fact_list, 'others': others}, 200

@app.route('/graph')
def graph():
    paper_title = request.args.get('paper_title')
    limit = request.args.get('limit', 30, type=int)
    
    if not paper_title:
        return jsonify({"msg": "Missing 'paper_title' parameter"}), 400
    
    graph = gs.query_graph(paper_title=paper_title, limit=limit)
    return {'graph': graph}, 200

@app.route('/kwGraph')
def kwGraph():
    keys = request.args.get('keys')
    paper_title = request.args.get('paper_title')
    limit = request.args.get('limit', 30, type=int)

    if not keys:
        return jsonify({"msg": "Missing 'keys' parameter"}), 400
    if not paper_title:
        jsonify({"msg": "Missing 'paper_title' parameter"}), 400

    try:
        processed_keywords = gs.text_preprocessing(keys, flatten=True)
    except:
        return jsonify({'msg': 'Database is not available'}), 503
        
    kwGraph = gs.query_graph_key_paper(keys=tuple(processed_keywords), paper_title=paper_title, limit=limit)
    return {'graph': kwGraph}, 200


if __name__ == '__main__':
    # app.run(debug=False)
    app.run(debug=False, port=8000, host='0.0.0.0') 
