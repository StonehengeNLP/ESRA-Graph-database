# Graph Database Manager

## API Documentation

The APIs can be accessed and tested via the swagger in http://localhost:8000/docs/

## Setting Up

1. Install dependencies by `pip install -r requirements.txt`
2. Run Neo4j and update `.env` file
3. Run `python add_data.py` to add the extracted scientific knowledge graph into the graph database (takes quite a long time)
4. Run `python cluster_and_drop.py` to drop some semantic/syntactic duplications
5. Run `python gen_vocab.py` to generate a replication of vocaburary from the graph database
6. Run `python app.py` to serve the endpoints (also generate a set of embedding vectors from the previous step if not exist)

## Initial Dataset

The following files contain many essential field using for constructing knowledge graph. You can modify the dataset and script to add more information to the graph.

##### 1. data/csv/kaggle-arxiv-cscl-2020-12-18.csv
Metadata of arxiv dataset retreived from [Cornell-University/arxiv](https://www.kaggle.com/Cornell-University/arxiv) filtering only Computation and Language (CL) category.

##### 2. data/pickle/kaggle_arxiv_cite_ref.pickle
Citations and references for each publication in the arxiv cs.CL dataset

##### 3. data/pickle/kaggle_arxiv_cleaned.pickle
The combination of retreived metadata from [Cornell-University/arxiv](https://www.kaggle.com/Cornell-University/arxiv) and additional essential fields
