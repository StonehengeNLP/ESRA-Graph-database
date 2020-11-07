import settings
import models
from neomodel import config, Q, db

username = settings.NEO4J_USERNAME
password = settings.NEO4J_PASSWORD
host = settings.NEO4J_HOST
port = settings.NEO4J_PORT


config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'

# class Book(StructuredNode):
#     title = StringProperty(unique_index=True)
#     author = RelationshipTo('Author', 'AUTHOR')

# class Author(StructuredNode):
#     name = StringProperty(unique_index=True)
#     books = RelationshipFrom('Book', 'AUTHOR')

# harry_potter = Book(title='Harry potter and the..').save()
# rowling =  Author(name='J. K. Rowling').save()
# harry_potter.author.connect(rowling)

# Author.nodes.filter(
#     Q(name__startswith='H')
# )

def deleteData():
    query = 'MATCH (n) DETACH DELETE n'
    db.cypher_query(query)

deleteData()


t = models.Task(name='Tong').save()
mc = models.Metric(name='Win').save()
md = models.Method(name='Pinn').save()

mc.task_partOf.connect(t)
md.metric_isA.connect(mc)

# for a in t.nodes:
#     print(a)

