# Graph Database Manager

## API documentation

The APIs can be accessed and tested via the swagger in http://localhost:8000/docs/

## Setting Up

1. Install dependencies by `pip install -r requirements.txt`
2. Run Neo4j and update `.env` file
3. Run `python add_data.py` to add the extracted scientific knowledge graph into the graph database (takes quite a long time)
4. Run `python cluster_and_drop.py` to drop some semantic/syntactic duplications
5. Run `python gen_vocab.py` to generate a replication of vocaburary from the graph database
6. Run `python app.py` to serve the endpoints (also generate a set of embedding vectors from the previous step if not exist)
