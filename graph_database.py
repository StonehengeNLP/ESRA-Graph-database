import settings
import models
from neomodel import config, Q, db

class GraphDatabase():

    def __init__(self):
        username = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        host = settings.NEO4J_HOST
        port = settings.NEO4J_PORT
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'

    def clear_all(self):
        query = 'MATCH (n) DETACH DELETE n'
        db.cypher_query(query)

    def add_entity(self):
        pass
    
    

# t = models.Task(name='tongtong').save()
# t = models.Task(name='tongtong').save()

# for a in t.nodes:
#     print(a)