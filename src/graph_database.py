"""
src.graph_database

This module is for communicating with Hosted Neo4j somewhere
I have prevented injection by putting the "key" as params when querying
some param like "paper_title" and "hops" are type-validated already

This might not be the best practice, so feel free to edit it
"""

import re
from . import settings
from . import models
from . import validator
from typing import List
from functools import lru_cache
from neomodel import config, db, match


class GraphDatabase():

    CYPHER_DELETE_ALL = "MATCH (n) DETACH DELETE n"
    CYPHER_CREATE_INDEX_1 = \
        """
        CREATE INDEX ON :BaseEntity(name)
        """
    CYPHER_CREATE_INDEX_2 = \
        """
        CREATE CONSTRAINT on (p:Paper)
        ASSERT p.name IS UNIQUE
        """
    CYPHER_CREATE_INDEX_3 = \
        """
        CREATE CONSTRAINT on (b:Paper)
        ASSERT b.arxiv_id IS UNIQUE
        """
    CYPHER_NODES_KEYS_PAPER = \
        """
        MATCH (n:BaseEntity)-[r1]-(m:BaseEntity)-[r2:appear_in]-(b:Paper)
        USING INDEX n:BaseEntity(name)
        USING INDEX b:Paper(name)
        WHERE n.name in $key_list 
            AND b.name = $paper_title
            AND NOT m:Paper
        WITH COLLECT(DISTINCT m.name) as out
        RETURN out
        """
    CYPHER_ONE_HOP = \
        """
        MATCH (n:BaseEntity)-[e]-(m)
        USING INDEX n:BaseEntity(name)
        WHERE n.name in $key_list
            AND NOT m:Paper
        RETURN DISTINCT
            n.best_variant as key,
            labels(n) as n_labels,
            n.count as n_count,
            e.weight as score,
            e.from_papers as papers,
            type(e) as type,
            startnode(e) = n as isSubject,
            m.best_variant as name,
            labels(m) as m_labels,
            m.count as m_count
        ORDER BY score DESC
        LIMIT $limit
        """
    CYPHER_ONE_HOP_WITH_PAPER_ALLOWED = \
        """
        MATCH (n:BaseEntity)-[e]-(m)
        USING INDEX n:BaseEntity(name)
        WHERE n.name in $key_list
        RETURN DISTINCT
            n.best_variant as key,
            labels(n) as n_labels,
            n.count as n_count,
            e.weight as score,
            e.from_papers as papers,
            type(e) as type,
            startnode(e) = n as isSubject,
            m.best_variant as name,
            labels(m) as m_labels,
            m.count as m_count
        ORDER BY score DESC
        LIMIT $limit
        """
    CYPHER_KEYWORD_GRAPH = \
        """
        MATCH (n)-[e]-(m)
        WHERE n.name in $key_list
            AND NOT m:Paper
        RETURN DISTINCT
            n.best_variant as key,
            labels(n) as n_labels,
            n.count as n_count,
            e.from_papers as papers,
            type(e) as type,
            startnode(e) = n as isSubject,
            m.best_variant as name,
            labels(m) as m_labels,
            m.count as m_count
        LIMIT $limit
        """
    # CYPHER_D3_QUERY = \
    #     """
    #     MATCH (n:Paper)
    #     USING INDEX n:Paper(name)
    #     WHERE n.name = $paper_title
    #     MATCH (n)-[r:appear_in]-(m)
    #     MATCH (n)-[t:appear_in]-(p)
    #     MATCH (m)<-[k]-(p)
    #     RETURN DISTINCT n.best_variant, labels(n), type(r), m.best_variant, labels(m), type(k), p.best_variant, labels(p)
    #     LIMIT $limit;
    #     """
    CYPHER_D3_QUERY_1 = \
        """MATCH (n:Paper)
        USING INDEX n:Paper(name)
        WHERE n.name = $paper_title
        MATCH (m)-[r:appear_in]->(n)
        WITH [m.best_variant, labels(m), type(r), n.best_variant, labels(n)] as out1
        RETURN DISTINCT out1
        LIMIT $limit;"""
    CYPHER_D3_QUERY_2 = \
        """MATCH (n:Paper)
        USING INDEX n:Paper(name)
        WHERE n.name = $paper_title
        MATCH (m)-[r:appear_in]->(n)
        MATCH (m)-[p]->(k)
        MATCH (k)-[r2]-(n)
        WHERE not k:Paper
        WITH [m.best_variant, labels(m), type(p), k.best_variant, labels(k)] as out2
        RETURN DISTINCT out2
        LIMIT $limit;"""
    CYPHER_D3_KEY_PAPER = \
        """
        MATCH (m:Paper)
        USING INDEX m:Paper(name)
        WHERE m.name = $paper_title
        MATCH (n:BaseEntity)
        USING INDEX n:BaseEntity(name)
        WHERE n.name in $key_list
        MATCH path = (n)-[*..2]-(m)-[k]-(p)
        WHERE type(k) <> 'cite'
        RETURN path 
        LIMIT $limit
        """
    CYPHER_SUM_ENTITY_COUNT = \
        """
        MATCH (m:BaseEntity)
        USING INDEX m:BaseEntity(name)
        WHERE m.name = $key
        RETURN sum(m.count)
        """
    
    def __init__(self):
        username = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        host = settings.NEO4J_HOST
        port = settings.NEO4J_PORT
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'
        self.create_indexes()
        
    def create_indexes(self):
        """
        Create all indexes to search faster in Neo4j
        """
        try: db.cypher_query(self.CYPHER_CREATE_INDEX_1)
        except: pass
        
        try: db.cypher_query(self.CYPHER_CREATE_INDEX_2)
        except: pass
        
        try: db.cypher_query(self.CYPHER_CREATE_INDEX_3)
        except: pass
        
        
    def clear_all(self):
        """
        Clear all nodes and relations
        ** Carefully use this method
        """
        db.cypher_query(self.CYPHER_DELETE_ALL)
        
    def get_entity_model(self, entity_type):
        return models.__dict__[entity_type]
        
    def get_all_entities(self, entity_type:str) -> List[models.BaseEntity]:
        entity_model = self.get_entity_model(entity_type)
        return entity_model.nodes.all()
    
    def get_entity(self, entity_type, **kwargs):
        entity_model = self.get_entity_model(entity_type)
        target_entity = entity_model.nodes.get(**kwargs)
        return target_entity
    
    def is_entity_exist(self, entity_type, **kwargs):
        entity_model = self.get_entity_model(entity_type)
        target_entity = entity_model.nodes.first_or_none(**kwargs)
        if target_entity == None:
            return False
        return True
    
    def add_entity(self, entity_type, entity_name, confidence=1, **kwargs):
        name_lower = entity_name.lower()
        if self.is_entity_exist(entity_type, name=name_lower):
            target_entity = self.get_entity(entity_type, name=name_lower)
            target_entity.count += 1

            if entity_name in target_entity.variants:
                target_entity.variants[entity_name] += 1
            elif target_entity.variants != None:
                target_entity.variants[entity_name] = 1
            else:
                target_entity.variants = {entity_name: 1}
                
            _weight_diff = (confidence - target_entity.weight) / target_entity.count
            target_entity.weight += _weight_diff
        else:
            entity_model = self.get_entity_model(entity_type)
            target_entity = entity_model(name=name_lower)
            target_entity.weight = confidence
            target_entity.variants = {entity_name: 1}
        
        target_entity.best_variant = max(target_entity.variants, key=target_entity.variants.get)
                
        target_entity.__dict__.update(kwargs)
        target_entity.save()
        return target_entity
    
    def count_entity(self, entity_name):
        res = db.cypher_query(self.CYPHER_SUM_ENTITY_COUNT, {'key': entity_name})
        return res
    
    def get_relation(self, relation_type, head_entity):
        assert isinstance(head_entity, models.BaseEntity)
        relation_type = relation_type.lower().replace('-', '_')
        relation = head_entity.__dict__[relation_type]
        return relation
    
    def is_relation_exist(self, relation_type, head_entity, tail_entity):
        assert isinstance(head_entity, models.BaseEntity)
        assert isinstance(tail_entity, models.BaseEntity)
        
        relation_type = relation_type.lower().replace('-', '_')
        relation = self.get_relation(relation_type, head_entity)
        relationship = relation.relationship(tail_entity)
        if relationship == None:
            return False
        return True
        
    def add_relation(self, relation_type, head_entity, tail_entity, confidence=1, from_paper=None, **kwargs):
        assert isinstance(head_entity, models.BaseEntity)
        assert isinstance(tail_entity, models.BaseEntity)
        
        relation_type = relation_type.lower().replace('-', '_')
        relation = self.get_relation(relation_type, head_entity)
        if self.is_relation_exist(relation_type, head_entity, tail_entity):
            relationship = relation.relationship(tail_entity)
            relationship.count += 1
            relationship.weight += confidence
        else:
            relationship = relation.connect(tail_entity)
            relationship.weight = confidence
        try:
            validator.validate_relation(relation_type, head_entity, tail_entity)
        except Exception as e:
            # print(e)
            relationship.flag_violation = True
        if from_paper != None:
            relationship.from_papers += [from_paper]
        relationship.__dict__.update(kwargs)
        relationship.save()
        return relationship
        
    def get_one_hops(self, keys: list, limit: int):
        # key = '|'.join(keys)
        results = db.cypher_query(self.CYPHER_ONE_HOP, {'key_list': list(keys), 'limit': limit})
        if len(results[0]) < 5:
            results = db.cypher_query(
                self.CYPHER_ONE_HOP_WITH_PAPER_ALLOWED, 
                {'key_list': list(keys), 'limit': limit}
            )
        return results
    
    def query_graph(self, paper_title: str, limit: int):
        """
        This function is for visualization in frontend using D3.js
        and use only 'CYPHER_D3_QUERY_1' and 'CYPHER_D3_QUERY_2'
        """
        paper_title = paper_title.lower()
        res_1 = db.cypher_query(self.CYPHER_D3_QUERY_1, {'paper_title': paper_title, 'limit': limit})
        res_2 = db.cypher_query(self.CYPHER_D3_QUERY_2, {'paper_title': paper_title, 'limit': limit})
        res = res_1[0] + res_2[0]
        get_label = lambda x: x[0] if x[0] != "BaseEntity" else x[1]
        relations = set()
        for row in res:
            n_name, n_labels, r, m_name, m_labels = row[0]
            n_labels = get_label(n_labels)
            m_labels = get_label(m_labels)
            ent_1 = (n_name, n_labels)
            ent_2 = (m_name, m_labels)
            r1 = (r, ent_1, ent_2)
            relations.add(r1)
            
        relations = list(relations)
        return relations 
    
    def query_graph_key_paper(self, keys, paper_title, limit):
        """
        Query path from keyword to paper node for visualize on frontend
        """
        # keys = '|'.join(keys).lower()
        paper_title = paper_title.lower()
        paths = db.cypher_query(
            self.CYPHER_D3_KEY_PAPER, 
            {'key_list': list(keys), 'paper_title':paper_title, 'limit': limit}
        )[0]

        new_paths = []
        get_label = lambda x: x[0] if x[0] != 'BaseEntity' else x[1]

        for path in paths:
            tmp_path = []
            for relation in path[0]._relationships:
                relation_type = relation.type
                
                start_node_name = relation._start_node._properties['best_variant']
                start_node_label = get_label(list(relation._start_node.labels))

                end_node_name = relation._end_node._properties['best_variant']
                end_node_label = get_label(list(relation._end_node.labels))

                tmp_path.append([
                    relation_type, 
                    (start_node_name, start_node_label,),
                    (end_node_name, end_node_label,)
                ])

            new_paths.append(tmp_path)
        
        return new_paths
    
    def query_keyword_graph(self, keys):
        """
        This function is for querying graph containing keywords and relation path regarding keywords
        and attached with fact list to visualize in search page
        """
        n = 30
        nodes = db.cypher_query(self.CYPHER_KEYWORD_GRAPH, {'key_list': list(keys), 'limit': n})
        return nodes
    
    @lru_cache(maxsize=128)
    def get_related_nodes(self, keys: tuple, paper_title: str, max_hops=2):
        """
        This function is for querying nodes and send it to summarization
        """
        # key = '|'.join(keys)
 
        query = self.CYPHER_NODES_KEYS_PAPER.format(hops=max_hops)
        nodes = db.cypher_query(query, {'key_list': list(keys), 'paper_title': paper_title})
        return nodes[0][0][0]
