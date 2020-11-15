import neomodel
from datetime import datetime

class BaseRelation(neomodel.StructuredRel):
    count = neomodel.IntegerProperty(default=1)
    weight = neomodel.FloatProperty(default=0)
    create_at = neomodel.DateTimeFormatProperty(format="%Y-%m-%d %H:%M:%S", default_now=True)

class HyponymOf(BaseRelation):
    pass

class FeatureOf(BaseRelation):
    pass

class UsedFor(BaseRelation):
    pass

class PartOf(BaseRelation):
    pass

class ReferTo(BaseRelation):
    pass

class Compare(BaseRelation):
    pass

class EvaluateFor(BaseRelation):
    pass

class AppearIn(BaseRelation):
    pass

class AuthorOf(BaseRelation):
    pass

class AffiliateWith(BaseRelation):
    pass

class Cite(BaseRelation):
    pass

class BaseEntity(neomodel.StructuredNode):
    name = neomodel.StringProperty(unique_index=True)
    count = neomodel.IntegerProperty(default=1)
    weight = neomodel.FloatProperty(default=0)
    create_at = neomodel.DateTimeFormatProperty(format="%Y-%m-%d %H:%M:%S", default_now=True)

    # GOD attributes: relation from head (self) to Tail (other)
    used_for = neomodel.RelationshipTo(neomodel.StructuredNode, 'used_for', model=UsedFor)
    part_of = neomodel.RelationshipTo(neomodel.StructuredNode, 'part_of', model=PartOf)
    feature_of = neomodel.RelationshipTo(neomodel.StructuredNode, 'feature_of', model=FeatureOf)
    compare = neomodel.RelationshipTo(neomodel.StructuredNode, 'compare', model=Compare)
    hyponym_of = neomodel.RelationshipTo(neomodel.StructuredNode, 'hyponym_of', model=HyponymOf)
    evaluate_for = neomodel.RelationshipTo(neomodel.StructuredNode, 'evaluate_for', model=EvaluateFor)
    refer_to = neomodel.RelationshipTo(neomodel.StructuredNode, 'refer_to', model=ReferTo)
    appear_in = neomodel.RelationshipTo(neomodel.StructuredNode, 'appear_in', model=AppearIn)
    author_of = neomodel.RelationshipTo(neomodel.StructuredNode, 'author_of', model=AuthorOf)
    affiliate_with = neomodel.RelationshipTo(neomodel.StructuredNode, 'affiliate_with', model=AffiliateWith)
    cite = neomodel.RelationshipTo(neomodel.StructuredNode, 'cite', model=Cite)
    
class Generic(BaseEntity):
    pass

class Task(BaseEntity):
    pass

class Method(BaseEntity):
    pass

class Material(BaseEntity):
    pass

class OtherScientificTerm(BaseEntity):
    pass

class Metric(BaseEntity):
    pass

class Abbreviation(BaseEntity):
    pass

class Paper(BaseEntity):
    mag_id = neomodel.IntegerProperty()
    cc = neomodel.IntegerProperty()

class Author(BaseEntity):
    pass

class Affiliation(BaseEntity):
    pass