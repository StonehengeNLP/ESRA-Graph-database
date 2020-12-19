import json
from src import graph_search as gs
from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/docs'
API_URL = '/swagger'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Test application"
    },
)
app.register_blueprint(swaggerui_blueprint)

@app.route('/swagger')
def swagger():
    with open('swagger.json') as f:
        swagger_json = json.load(f)
        return swagger_json
    
@app.route('/complete')
def complete():
    query = request.args.get("q")
    if not query:
        return jsonify({"msg": "Missing query parameter"}), 400
    
    tokenized_text = query.split()
    for i in range(len(tokenized_text)):
        temp_text = ' '.join(tokenized_text[i:])
        out = gs.text_autocomplete(temp_text)
        if out:
            n_skip = temp_text.count(' ')
            out = [' '.join(word.split()) for word in out]
            break
    return {'sentences': out}
    
    papers = gs.search(query, mode='popularity')
    response = {'papers': papers}
    return response

if __name__ == '__main__':
    app.run(debug=True)