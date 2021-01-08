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
from neomodel import config, db, match


class GraphDatabase():

    CYPHER_DELETE_ALL = "MATCH (n) DETACH DELETE n"
    CYPHER_GRAPH_CHECK = "CALL gds.graph.exists( $graph_name )"
    CYPHER_GRAPH_CREATE = \
        """ CALL gds.graph.create.cypher(
                $graph_name,
                'MATCH (n)-[e *0..2]-(m) \
                    WHERE m.name =~ $key \
                    RETURN distinct(id(n)) AS id',
                'MATCH (n)-[e]-(m) \
                    RETURN id(n) AS source, e.weight AS weight, id(m) AS target',
                {{validateRelationships: false}}
            )
        """
    CYPHER_GRAPH_DELETE = "CALL gds.graph.drop($graph_name)"
    CYPHER_PAGE_RANK = \
        """ MATCH (n)
            WHERE n.name =~ $key
            CALL gds.pageRank.stream( $graph_name, {{
                maxIterations: 20,
                dampingFactor: 0.85,
                relationshipWeightProperty: 'weight',
                sourceNodes: [n]
            }})
            YIELD nodeId, score WITH gds.util.asNode(nodeId) as node, score
            WHERE node:Paper
            RETURN DISTINCT
                sum(score) AS score,
                node.cc,
                node.name
            ORDER BY score DESC
        """
    CYPHER_CHECK_NODE_EXIST = "MATCH (n) WHERE n.name =~ $key RETURN count(n);"
    CYPHER_PATH_KEYS_PAPER = \
        """ MATCH (m)
            WHERE m.name =~ $paper_title
            MATCH path1 = (x)-[r1:appear_in]->(m)
            WITH COLLECT(x.name) + COLLECT(m.name) as local_nodes, m
            MATCH path2 = (n)-[*..{hops}]-(m)
            WHERE n.name =~ $key
                AND ALL(node in nodes(path2) WHERE node.name in local_nodes)
            RETURN DISTINCT path2
        """
    CYPHER_NODES_KEYS_PAPER = \
        """ MATCH (m)
            WHERE m.name =~ $paper_title
            MATCH path1 = (x)-[r1:appear_in]->(m)
            WITH COLLECT(x.name) + COLLECT(m.name) as local_nodes, m
            MATCH path2 = (n)-[*..{hops}]-(m)
            WHERE n.name =~ $key
                AND ALL(node in nodes(path2) WHERE node.name in local_nodes)
            MATCH (q)
            WHERE q IN nodes(path2)
            WITH COLLECT(DISTINCT q.name) as out
            RETURN out
        """
    CYPHER_ONE_HOP = \
        """
            MATCH (n)-[e]-(m)
            WHERE n.name =~ $key
                AND NOT m:Paper
            RETURN DISTINCT
                n.name as key,
                round(e.weight,4) as score,
                type(e) as type,
                startnode(e) = n as isSubject,
                m.name as name
            ORDER BY score DESC
            LIMIT 10
        """
    CYPHER_D3_QUERY = \
        """
        MATCH (n)
        WHERE n.name =~ $key
        MATCH (m)
        WHERE m.name = $paper_title
        MATCH path = (n)-[*..2]-(m)-[k]-(p)
        WHERE type(k) <> 'cite'
        RETURN path
        LIMIT $limit
        """
    
    def __init__(self):
        username = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        host = settings.NEO4J_HOST
        port = settings.NEO4J_PORT
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'

    def clear_all(self):
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
        if self.is_entity_exist(entity_type, name=entity_name):
            target_entity = self.get_entity(entity_type, name=entity_name)
            target_entity.count += 1
            _weight_diff = (confidence - target_entity.weight) / target_entity.count
            target_entity.weight += _weight_diff
        else:
            entity_model = self.get_entity_model(entity_type)
            target_entity = entity_model(name=entity_name)
            target_entity.weight = confidence
        target_entity.__dict__.update(kwargs)
        target_entity.save()
        return target_entity
    
    def count_entity(self, entity_name):
        base_entity = self.get_entity_model('BaseEntity')
        nodes = base_entity.nodes.filter(name__iexact=entity_name)
        return sum([n.count for n in nodes])
    
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
        
    def add_relation(self, relation_type, head_entity, tail_entity, confidence=1, **kwargs):
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
        relationship.__dict__.update(kwargs)
        relationship.save()
        return relationship
        
    def is_node_exist(self, key):
        """ Check if node exist before searching """
        exist = (db.cypher_query(self.CYPHER_CHECK_NODE_EXIST, {'key': key})[0][0][0])
        return True if exist else False

    def is_cypher_graph_exist(self, keys: list):
        graph_name = ''.join(keys)
        is_exist = db.cypher_query(self.CYPHER_GRAPH_CHECK, {'graph_name': graph_name})[0][0][1]
        return is_exist
    
    def create_cypher_graph(self, keys: list):
        graph_name = ''.join(keys)
        key = '|'.join(keys)
        db.cypher_query(self.CYPHER_GRAPH_CREATE, {'graph_name': graph_name, 'key': key})
    
    def delete_cypher_graph(self, keys: list):
        graph_name = ''.join(keys)
        db.cypher_query(self.CYPHER_GRAPH_DELETE, {'graph_name': graph_name})
    
    def pagerank(self, keys: list):
        graph_name = ''.join(keys)
        key = '|'.join(keys)
        results = db.cypher_query(self.CYPHER_PAGE_RANK, {'key': key, 'graph_name': graph_name})[0]
        return results
    
    def get_paths(self, keys: list, paper_title: str, local=True, max_hops=3):
        """
        Retrieve paths from given keys to target paper
        use only CYPHER_PATH_KEYS_PAPER
        
        :param keys: list of preprocessed keys
        :param paper_title: the title name of target paper
        :param local: all retrieved entities will be from the paper (local graph)
        :param max_hops: maximum number of hops will be returned
        
        :return: path from keys to paper_title
        """
        key = '|'.join(keys)
 
        query = self.CYPHER_PATH_KEYS_PAPER.format(hops=max_hops)
        paths = db.cypher_query(query, {'key': key, 'paper_title': paper_title})[0]

        new_paths = []
        for path in paths:
            temp_path = []
            for j in path[0]._relationships:
                relation_type = j.type
                relation_weight = j._properties['weight']
                start_node = j._start_node._properties['name']
                start_node_class = list(j._start_node.labels)
                start_node_class = [label for label in start_node_class if label != 'BaseEntity']
                end_node = j._end_node._properties['name']
                end_node_class = list(j._end_node.labels)
                end_node_class = [label for label in end_node_class if label != 'BaseEntity']
                temp_path.append([relation_type, relation_weight, (start_node, start_node_class), (end_node, end_node_class)])
            new_paths.append(temp_path)
        return new_paths

    def get_one_hops(self, keys: list):
        key = '|'.join(keys)
        results = db.cypher_query(self.CYPHER_ONE_HOP, {'key': key})
        return results
    
    def query_graph(self, keys: list, paper_title: str, limit: int):
        """
        This function is for visualization in frontend using D3.js
        and use only 'CYPHER_D3_QUERY'
        """
        key = '|'.join(keys).lower()
        paper_title = paper_title.lower()
        paths = db.cypher_query(self.CYPHER_D3_QUERY, {'key': key, 'paper_title': paper_title, 'limit': limit})[0]
    
        new_paths = []
        for path in paths:
            temp_path = []
            for j in path[0]._relationships:
                relation_type = j.type
                start_node = j._start_node._properties['name']
                start_node_class = list(j._start_node.labels)
                start_node_class = [label for label in start_node_class if label != 'BaseEntity'][0]
                end_node = j._end_node._properties['name']
                end_node_class = list(j._end_node.labels)
                end_node_class = [label for label in end_node_class if label != 'BaseEntity'][0]
                temp_path.append([relation_type, (start_node, start_node_class), (end_node, end_node_class)])
            new_paths.append(temp_path)
        return new_paths
        
    def get_related_nodes(self, keys: list, paper_title: str, max_hops=3):
        """
        This function is for querying nodes and send it to summarization
        """
        key = '|'.join(keys)
 
        query = self.CYPHER_NODES_KEYS_PAPER.format(hops=max_hops)
        nodes = db.cypher_query(query, {'key': key, 'paper_title': paper_title})
        return nodes[0][0][0]