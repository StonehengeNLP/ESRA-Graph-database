from . import settings
from . import models
from . import validator
from neomodel import config, Q, db
from typing import List

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

    @classmethod
    def get_entity_model(cls, entity_type):
        return models.__dict__[entity_type]
        
    def get_all_entities(self, entity_type:str) -> List[models.BaseEntity]:
        entity_model = GraphDatabase.get_entity_model(entity_type)
        return entity_model.nodes.all()
    
    def get_entity(self, entity_type, **kwargs):
        entity_model = GraphDatabase.get_entity_model(entity_type)
        target_entity = entity_model.nodes.get(**kwargs)
        return target_entity
    
    def is_entity_exist(self, entity_type, **kwargs):
        entity_model = GraphDatabase.get_entity_model(entity_type)
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
            entity_model = GraphDatabase.get_entity_model(entity_type)
            target_entity = entity_model(name=entity_name)
            target_entity.weight = confidence
        target_entity.__dict__.update(kwargs)
        target_entity.save()
        return target_entity
    
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
            print(e)
            relationship.flag_violation = True
        relationship.__dict__.update(kwargs)
        relationship.save()
        return relationship