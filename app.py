from src import graph_search as gs
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/test')
def test():
    return 'test'

@app.route('/', methods=['POST'])
def fetch_query():
    query = request.json.get('query', None)
    if not query:
        return jsonify({"msg": "Missing query parameter"}), 400
    
    tokenized_text = query.split()
    for i in range(len(tokenized_text)):
        temp_text = ' '.join(tokenized_text[i:])
        out = gs.text_autocomplete(temp_text)
        if out:
            n_skip = temp_text.count(' ')
            out = [' '.join(word.split()[n_skip:]) for word in out]
            break
    return out
    
    papers = gs.search(query, mode='popularity')
    response = {'papers': papers}
    return response

if __name__ == '__main__':
    app.run(debug=True)