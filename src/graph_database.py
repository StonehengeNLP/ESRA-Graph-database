from . import settings
from . import models
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
    
    def is_relation_exist(self, relation_type, head_entity, tail_entity):
        assert isinstance(head_entity, models.BaseEntity)
        assert isinstance(tail_entity, models.BaseEntity)
        if relation_type == 'Hyponym-of':
            relationship = head_entity.hyponym_of.relationship(tail_entity)
        elif relation_type == 'Feature-of':
            relationship = head_entity.feature_of.relationship(tail_entity)
        elif relation_type == 'Used-for':
            relationship = head_entity.used_for.relationship(tail_entity)
        elif relation_type == 'Part-of':
            relationship = head_entity.part_of.relationship(tail_entity)
        elif relation_type == 'Refer-to':
            relationship = head_entity.refer_to.relationship(tail_entity)
        elif relation_type == 'Compare':
            relationship = head_entity.compare.relationship(tail_entity)
        elif relation_type == 'Evaluate-for':
            relationship = head_entity.evaluate_for.relationship(tail_entity)
        elif relation_type == 'Is-a':
            relationship = head_entity.is_a.relationship(tail_entity)
        elif relation_type == 'Appear-in':
            relationship = head_entity.appear_in.relationship(tail_entity)
        elif relation_type == 'Author-of':
            relationship = head_entity.author_of.relationship(tail_entity)
        elif relation_type == 'In-category':
            relationship = head_entity.in_category.relationship(tail_entity)
        if relationship == None:
            return False
        return True
        
    def add_relation(self, relation_type, head_entity, tail_entity, confidence=1, **kwargs):
        assert isinstance(head_entity, models.BaseEntity)
        assert isinstance(tail_entity, models.BaseEntity)
        
        if relation_type == 'Hyponym-of':
            head_relation = head_entity.hyponym_of
        elif relation_type == 'Feature-of':
            head_relation = head_entity.feature_of
        elif relation_type == 'Used-for':
            head_relation = head_entity.used_for
        elif relation_type == 'Part-of':
            head_relation = head_entity.part_of
        elif relation_type == 'Refer-to':
            head_relation = head_entity.refer_to
        elif relation_type == 'Compare':
            head_relation = head_entity.compare
        elif relation_type == 'Evaluate-for':
            head_relation = head_entity.evaluate_for
        elif relation_type == 'Is-a':
            head_relation = head_entity.is_a
        elif relation_type == 'Appear-in':
            head_relation = head_entity.appear_in
        elif relation_type == 'Author-of':
            head_relation = head_entity.author_of
        elif relation_type == 'In-category':
            head_relation = head_entity.in_category
            
        if self.is_relation_exist(relation_type, head_entity, tail_entity):
            relationship = head_relation.relationship(tail_entity)
            relationship.count += 1
            _weight_diff = (confidence - relationship.weight) / relationship.count
            relationship.weight += _weight_diff
        else:
            relationship = head_relation.connect(tail_entity)
            relationship.weight = confidence
        relationship.__dict__.update(kwargs)
        relationship.save()
        return relationship