import settings
import models
from neomodel import config, Q, db

class GraphDatabase():
    
    ENTITY_MODEL = {
        'Task': models.Task,
        'Method': models.Method,
        'Material': models.Material,
        'OtherScientificTerm': models.OtherScientificTerm,
        'Metric': models.Metric,
        'Generic': models.Generic,
        'Abbreviation': models.Abbreviation,
        'Paper': models.Paper,
        }
    
    RELATION_MODEL = {
        'Hyponym-of': models.HyponymOf,
        'Feature-of': models.FeatureOf,
        'Used-for': models.UsedFor,
        'Part-of': models.PartOf,
        'Refer-to': models.ReferTo,
        'Compare': models.Compare,
        'Evaluate-for': models.EvaluateFor,
    }

    def __init__(self):
        username = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        host = settings.NEO4J_HOST
        port = settings.NEO4J_PORT
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'

    def clear_all(self):
        query = 'MATCH (n) DETACH DELETE n'
        db.cypher_query(query)

    def get_entity(self, entity_type, entity_name):
        entity_model = GraphDatabase.ENTITY_TYPE_MAP[entity_type]
        target_entity = entity_model.nodes.get(name=entity_name)
        return target_entity
    
    def is_entity_exist(self, entity_type, entity_name):
        entity_model = GraphDatabase.ENTITY_TYPE_MAP[entity_type]
        target_entity = entity_model.nodes.first_or_none(name=entity_name)
        if target_entity == None:
            return False
        return True
    
    def add_entity(self, entity_type, entity_name):
        if self.is_entity_exist(entity_type, entity_name):
            target_entity = self.get_entity(entity_type, entity_name)
            target_entity.count += 1
        else:
            target_entity = entity_model(name=entity_name).save()
        return target_entity
    
    def is_relation_exist(self, relation_type, relation_name, entity_1, entity_2):
        assert isinstance(entity_1, models.BaseEntity)
        assert isinstance(entity_2, models.BaseEntity)
        # relation_model = GraphDatabase.RELATION_MODEL[relation_type]
        # target_relation = relation_model.nodes.first_or_none(name=relation_name)
        # if target_relation == None:
        #     return False
        # return True
    
    def add_relation(self, relation_type, relation_name, entity_1, entity_2):
        assert isinstance(entity_1, models.BaseEntity)
        assert isinstance(entity_2, models.BaseEntity)
        # self.is_relation_exist(relation_type, relation_name, entity_1, entity_2)
