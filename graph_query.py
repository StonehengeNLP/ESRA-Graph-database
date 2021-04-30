
from src import graph_database as gdb
from neomodel import config, db

CYPHER_ONE_HOP = \
        """
        MATCH (n:BaseEntity)-[e]-(m)
        USING INDEX n:BaseEntity(name)
        WHERE n.name = $key
            AND NOT m:Paper
        RETURN DISTINCT
            n.best_variant as key,
            labels(n) as n_labels,
            e.weight * size(n.name) as score,
            e.from_papers as papers,
            type(e) as type,
            startnode(e) = n as isSubject,
            m.best_variant as name,
            labels(m) as m_labels
        ORDER BY score DESC
        LIMIT 10
        """
        
graph = gdb.GraphDatabase()
results = db.cypher_query(CYPHER_ONE_HOP, {'key': 'explainable ai'})
print(results)