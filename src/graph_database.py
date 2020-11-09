from . import settings
from . import models
from neomodel import config, Q, db
from typing import List

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
        'Author': models.Author,
        'Category': models.Category,
        }
    
    # RELATION_MODEL = {
    #     'Hyponym-of': models.HyponymOf,
    #     'Feature-of': models.FeatureOf,
    #     'Used-for': models.UsedFor,
    #     'Part-of': models.PartOf,
    #     'Refer-to': models.ReferTo,
    #     'Compare': models.Compare,
    #     'Evaluate-for': models.EvaluateFor,
    #     'Is-a': models.IsA,
    #     'Appear-in': models.AppearIn,
    # }

    def __init__(self):
        username = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        host = settings.NEO4J_HOST
        port = settings.NEO4J_PORT
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'

    def clear_all(self):
        query = 'MATCH (n) DETACH DELETE n'
        db.cypher_query(query)

    def get_all_entities(self, entity_type:str) -> List[models.BaseEntity]:
        entity_model = GraphDatabase.ENTITY_MODEL.get(
            entity_type, 
            models.BaseEntity
        )
        return entity_model.nodes.all()
        
    def get_entity(self, entity_type, entity_name):
        entity_model = GraphDatabase.ENTITY_MODEL[entity_type]
        target_entity = entity_model.nodes.get(name=entity_name)
        return target_entity
    
    def is_entity_exist(self, entity_type, entity_name):
        entity_model = GraphDatabase.ENTITY_MODEL[entity_type]
        target_entity = entity_model.nodes.first_or_none(name=entity_name)
        if target_entity == None:
            return False
        return True
    
    def add_entity(self, entity_type, entity_name, confidence=1, **kwargs):
        if self.is_entity_exist(entity_type, entity_name):
            target_entity = self.get_entity(entity_type, entity_name)
            target_entity.count += 1
            _weight_diff = (confidence - target_entity.weight) / target_entity.count
            target_entity.weight += _weight_diff
        else:
            entity_model = GraphDatabase.ENTITY_MODEL[entity_type]
            target_entity = entity_model(name=entity_name)
            target_entity.weight = confidence
        target_entity.__dict__.update(kwargs)
        target_entity.save()
        return target_entity
    
    def get_relation(self, relation_type, head_entity):
        assert isinstance(head_entity, models.BaseEntity)
        if relation_type == 'Hyponym-of':
            relation = head_entity.hyponym_of
        elif relation_type == 'Feature-of':
            relation = head_entity.feature_of
        elif relation_type == 'Used-for':
            relation = head_entity.used_for
        elif relation_type == 'Part-of':
            relation = head_entity.part_of
        elif relation_type == 'Refer-to':
            relation = head_entity.refer_to
        elif relation_type == 'Compare':
            relation = head_entity.compare
        elif relation_type == 'Evaluate-for':
            relation = head_entity.evaluate_for
        elif relation_type == 'Is-a':
            relation = head_entity.is_a
        elif relation_type == 'Appear-in':
            relation = head_entity.appear_in
        elif relation_type == 'Author-of':
            relation = head_entity.author_of
        elif relation_type == 'In-category':
            relation = head_entity.in_category
        return relation
    
    def is_relation_exist(self, relation_type, head_entity, tail_entity):
        assert isinstance(head_entity, models.BaseEntity)
        assert isinstance(tail_entity, models.BaseEntity)
        
        relation = self.get_relation(relation_type, head_entity)
        relationship = relation.relationship(tail_entity)
        if relationship == None:
            return False
        return True
        
    def add_relation(self, relation_type, head_entity, tail_entity, confidence=1, **kwargs):
        assert isinstance(head_entity, models.BaseEntity)
        assert isinstance(tail_entity, models.BaseEntity)
        
        relation = self.get_relation(relation_type, head_entity)
        if self.is_relation_exist(relation_type, head_entity, tail_entity):
            relationship = relation.relationship(tail_entity)
            relationship.count += 1
            relationship.weight += confidence
        else:
            relationship = relation.connect(tail_entity)
            relationship.weight = confidence
        relationship.__dict__.update(kwargs)
        relationship.save()
        return relationship