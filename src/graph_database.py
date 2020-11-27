from . import settings
from . import models
from . import validator
from typing import List
from fuzzywuzzy import fuzz
from neomodel import config, db, Q, match


class GraphDatabase():

    def __init__(self):
        username = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        host = settings.NEO4J_HOST
        port = settings.NEO4J_PORT
        config.DATABASE_URL = f'bolt://{username}:{password}@{host}:{port}'

    def clear_all(self):
        QUERY = 'MATCH (n) DETACH DELETE n'
        db.cypher_query(QUERY)

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
    
    def text_autocomplete(self, text, n=10):
        """suggest top 10 similar keywords based on the given text"""
        base_entity = GraphDatabase.get_entity_model('BaseEntity')
        nodes = base_entity.nodes.filter(name__istartswith=text.lower())
        suggested_list = list({node.name.lower() for node in nodes[:100]})
        return sorted(suggested_list, key=len)[:n]
    
    def text_correction(self, text, limit=1000):
        """correct the text to be matched to a node"""
        text = text.lower()
        base_entity = GraphDatabase.get_entity_model('BaseEntity')
        # match the first or second character 
        nodes = base_entity.nodes.filter(
            Q(name__istartswith=text[0]) | Q(name__regex=rf'^.{text[1]}.*'))
        suggested_list = list({node.name.lower() for node in nodes[:limit]})
        score = lambda x: fuzz.ratio(text, x.lower())
        best = max(suggested_list, key=score)
        # cut-off threshold 
        if score(best) < 60:
            return []
        return [best]
    
    def _score(self, path:list) -> int:
        """revise this function"""
        assert 'Paper' in path[-1].labels
        score = 1
        for i, x in enumerate(path):
            if i % 2 == 0:
                x = models.BaseEntity.inflate(x)
                score *= x.weight
            else:
                x = models.BaseRelation.inflate(x)
                score *= x.weight / x.count
        return score
    
    # TODO: prevent injection
    def search(self, key, hops=3):
        for h in range(1, 1 + hops):
            mat = ''.join([f'-[r{i+1}]-(n{i+1})' for i in range(h)])
            ret = ''.join([f', r{i+1}, n{i+1}' for i in range(h)])
            # not_aff = ' '.join([f'AND NOT n{i+1}:Affiliation' for i in range(h)])
            query = f"""MATCH (n:BaseEntity){mat} 
                        WHERE n.name =~ "(?i){key}"
                        AND n{h}:Paper 
                        RETURN DISTINCT n{ret};"""
                        # {not_aff}
            results = db.cypher_query(query)[0]
            print(len(results))
            x = sorted(results, key=self._score)[-10:]
            if len(x) > 0:
                for i in x:
                    en = models.BaseEntity.inflate(i[-1])
                    print(self._score(i), en.name)
            print('*'*100)
        return results