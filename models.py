import neomodel
import datetime
from neomodel.properties import *

class BaseEntity(neomodel.StructuredNode):
    name = neomodel.StringProperty(unique_index=True)
    create_at = DateTimeProperty(
        default=datetime.now() # no specific timezone 
    )

    #relation from Task to ...
    task_usedFor = neomodel.RelationshipTo('Task', 'Used-for',model=UsedFor)
    task_partOf = neomodel.RelationshipTo('Task', 'Part-of',model=PartOf)
    task_featureOf = neomodel.RelationshipTo('Task', 'Feature-of',model=FeatureOf)
    task_compare = neomodel.RelationshipTo('Task', 'Compare',model=Compare)
    task_hyponymOf = neomodel.RelationshipTo('Task', 'Hyponym-of',model=HyponymOf)
    task_evaluateFor = neomodel.RelationshipTo('Task', 'Evaluate-for',model=EvaluateFor)
    task_referTo = neomodel.RelationshipTo('Task', 'Refer-to',model=ReferTo)
    task_isA = neomodel.RelationshipTo('Task', 'Is-a',model=IsA)
    task_appearIn = neomodel.RelationshipTo('Task', 'Appear-in',model=AppearIn)

    # relation from method to ...
    method_usedFor = neomodel.RelationshipTo('Method', 'Used-for',model=UsedFor)
    method_partOf = neomodel.RelationshipTo('Method', 'Part-of',model=PartOf)
    method_featureOf = neomodel.RelationshipTo('Method', 'Feature-of',model=FeatureOf)
    method_compare = neomodel.RelationshipTo('Method', 'Compare',model=Compare)
    method_hyponymOf = neomodel.RelationshipTo('Method', 'Hyponym-of',model=HyponymOf)
    method_evaluateFor = neomodel.RelationshipTo('Method', 'Evaluate-for',model=EvaluateFor)
    method_referTo = neomodel.RelationshipTo('Method', 'Refer-to',model=ReferTo)
    method_isA = neomodel.RelationshipTo('Method', 'Is-a',model=IsA)
    method_appearIn = neomodel.RelationshipTo('Method', 'Appear-in',model=AppearIn)

    #relation from Material to ... 
    material_usedFor = neomodel.RelationshipTo('Material', 'Used-for')
    material_partOf = neomodel.RelationshipTo('Material', 'Part-of')
    material_featureOf = neomodel.RelationshipTo('Material', 'Feature-of')
    material_compare = neomodel.RelationshipTo('Material', 'Compare')
    material_hyponymOf = neomodel.RelationshipTo('Material', 'Hyponym-of')
    material_evaluateFor = neomodel.RelationshipTo('Material', 'Evaluate-for')
    material_referTo = neomodel.RelationshipTo('Material', 'Refer-to')
    material_isA = neomodel.RelationshipTo('Material', 'Is-a')
    material_appearIn = neomodel.RelationshipTo('Material', 'Appear-in')

    #relation from OtherScientificTerm to ... 
    otherScientificTerm_usedFor = neomodel.RelationshipTo('OtherScientificTerm', 'Used-for')
    otherScientificTerm_partOf = neomodel.RelationshipTo('OtherScientificTerm', 'Part-of')
    otherScientificTerm_featureOf = neomodel.RelationshipTo('OtherScientificTerm', 'Feature-of')
    otherScientificTerm_compare = neomodel.RelationshipTo('OtherScientificTerm', 'Compare')
    otherScientificTerm_hyponymOf = neomodel.RelationshipTo('OtherScientificTerm', 'Hyponym-of')
    otherScientificTerm_evaluateFor = neomodel.RelationshipTo('OtherScientificTerm', 'Evaluate-for')
    otherScientificTerm_referTo = neomodel.RelationshipTo('OtherScientificTerm', 'Refer-to')
    otherScientificTerm_isA = neomodel.RelationshipTo('OtherScientificTerm', 'Is-a')
    otherScientificTerm_appearIn = neomodel.RelationshipTo('OtherScientificTerm', 'Appear-in')

    #relation from Metric to ... 
    metric_usedFor = neomodel.RelationshipTo('Metric', 'Used-for')
    metric_partOf = neomodel.RelationshipTo('Metric', 'Part-of')
    metric_featureOf = neomodel.RelationshipTo('Metric', 'Feature-of')
    metric_compare = neomodel.RelationshipTo('Metric', 'Compare')
    metric_hyponymOf = neomodel.RelationshipTo('Metric', 'Hyponym-of')
    metric_evaluateFor = neomodel.RelationshipTo('Metric', 'Evaluate-for')
    metric_referTo = neomodel.RelationshipTo('Metric', 'Refer-to')
    metric_isA = neomodel.RelationshipTo('Metric', 'Is-a')
    metric_appearIn = neomodel.RelationshipTo('Metric', 'Appear-in')

    #relation from Generic to ... 
    generic_usedFor = neomodel.RelationshipTo('Generic', 'Used-for')
    generic_partOf = neomodel.RelationshipTo('Generic', 'Part-of')
    generic_featureOf = neomodel.RelationshipTo('Generic', 'Feature-of')
    generic_compare = neomodel.RelationshipTo('Generic', 'Compare')
    generic_hyponymOf = neomodel.RelationshipTo('Generic', 'Hyponym-of')
    generic_evaluateFor = neomodel.RelationshipTo('Generic', 'Evaluate-for')
    generic_referTo = neomodel.RelationshipTo('Generic', 'Refer-to')
    generic_isA = neomodel.RelationshipTo('Generic', 'Is-a')
    generic_appearIn = neomodel.RelationshipTo('Generic', 'Appear-in')

    #relation from Abbreviation to ... 
    abbreviation_usedFor = neomodel.RelationshipTo('Abbreviation', 'Used-for')
    abbreviation_partOf = neomodel.RelationshipTo('Abbreviation', 'Part-of')
    abbreviation_featureOf = neomodel.RelationshipTo('Abbreviation', 'Feature-of')
    abbreviation_compare = neomodel.RelationshipTo('Abbreviation', 'Compare')
    abbreviation_hyponymOf = neomodel.RelationshipTo('Abbreviation', 'Hyponym-of')
    abbreviation_evaluateFor = neomodel.RelationshipTo('Abbreviation', 'Evaluate-for')
    abbreviation_referTo = neomodel.RelationshipTo('Abbreviation', 'Refer-to')
    abbreviation_isA = neomodel.RelationshipTo('Abbreviation', 'Is-a')
    abbreviation_appearIn = neomodel.RelationshipTo('Abbreviation', 'Appear-in')

    #relation from Paper to ... 
    paper_usedFor = neomodel.RelationshipTo('Paper', 'Used-for')
    paper_partOf = neomodel.RelationshipTo('Paper', 'Part-of')
    paper_featureOf = neomodel.RelationshipTo('Paper', 'Feature-of')
    paper_compare = neomodel.RelationshipTo('Paper', 'Compare')
    paper_hyponymOf = neomodel.RelationshipTo('Paper', 'Hyponym-of')
    paper_evaluateFor = neomodel.RelationshipTo('Paper', 'Evaluate-for')
    paper_referTo = neomodel.RelationshipTo('Paper', 'Refer-to')
    paper_isA = neomodel.RelationshipTo('Paper', 'Is-a')
    paper_appearIn = neomodel.RelationshipTo('Paper', 'Appear-in')
    
class Task(BaseEntity):
    task_usedFor = neomodel.RelationshipTo('Task', 'Used-for',model=UsedFor)
    task_partOf = neomodel.RelationshipTo('Task', 'Part-of',model=PartOf)
    task_featureOf = neomodel.RelationshipTo('Task', 'Feature-of',model=FeatureOf)
    task_compare = neomodel.RelationshipTo('Task', 'Compare',model=Compare)
    task_hyponymOf = neomodel.RelationshipTo('Task', 'Hyponym-of',model=HyponymOf)
    task_evaluateFor = neomodel.RelationshipTo('Task', 'Evaluate-for',model=EvaluateFor)
    # task_referTo = neomodel.RelationshipTo('Task', 'Refer-to',model=ReferTo)
    task_isA = neomodel.RelationshipTo('Task', 'Is-a',model=IsA)
    task_appearIn = neomodel.RelationshipTo('Task', 'Appear-in',model=AppearIn)

class Method(BaseEntity):
    method_usedFor = neomodel.RelationshipTo('Method', 'Used-for',model=UsedFor)
    method_partOf = neomodel.RelationshipTo('Method', 'Part-of',model=PartOf)
    method_featureOf = neomodel.RelationshipTo('Method', 'Feature-of',model=FeatureOf)
    method_compare = neomodel.RelationshipTo('Method', 'Compare',model=Compare)
    method_hyponymOf = neomodel.RelationshipTo('Method', 'Hyponym-of',model=HyponymOf)
    method_evaluateFor = neomodel.RelationshipTo('Method', 'Evaluate-for',model=EvaluateFor)
    # method_referTo = neomodel.RelationshipTo('Method', 'Refer-to',model=ReferTo)
    method_isA = neomodel.RelationshipTo('Method', 'Is-a',model=IsA)
    method_appearIn = neomodel.RelationshipTo('Method', 'Appear-in',model=AppearIn)


class Material(BaseEntity):
    material_usedFor = neomodel.RelationshipTo('Material', 'Used-for',model=UsedFor)
    material_partOf = neomodel.RelationshipTo('Material', 'Part-of',model=PartOf)
    material_featureOf = neomodel.RelationshipTo('Material', 'Feature-of',model=FeatureOf)
    material_compare = neomodel.RelationshipTo('Material', 'Compare',model=Compare)
    material_hyponymOf = neomodel.RelationshipTo('Material', 'Hyponym-of',model=HyponymOf)
    material_evaluateFor = neomodel.RelationshipTo('Material', 'Evaluate-for',model=EvaluateFor)
    # material_referTo = neomodel.RelationshipTo('Material', 'Refer-to',model=ReferTo)
    material_isA = neomodel.RelationshipTo('Material', 'Is-a',model=IsA)
    material_appearIn = neomodel.RelationshipTo('Material', 'Appear-in',model=AppearIn)

class OtherScientificTerm(BaseEntity):
    otherScientificTerm_usedFor = neomodel.RelationshipTo('OtherScientificTerm', 'Used-for',model=UsedFor)
    otherScientificTerm_partOf = neomodel.RelationshipTo('OtherScientificTerm', 'Part-of',model=PartOf)
    otherScientificTerm_featureOf = neomodel.RelationshipTo('OtherScientificTerm', 'Feature-of',model=FeatureOf)
    otherScientificTerm_compare = neomodel.RelationshipTo('OtherScientificTerm', 'Compare',model=Compare)
    otherScientificTerm_hyponymOf = neomodel.RelationshipTo('OtherScientificTerm', 'Hyponym-of',model=HyponymOf)
    otherScientificTerm_evaluateFor = neomodel.RelationshipTo('OtherScientificTerm', 'Evaluate-for',model=EvaluateFor)
    # otherScientificTerm_referTo = neomodel.RelationshipTo('OtherScientificTerm', 'Refer-to',model=ReferTo)
    otherScientificTerm_isA = neomodel.RelationshipTo('OtherScientificTerm', 'Is-a',model=IsA)
    otherScientificTerm_appearIn = neomodel.RelationshipTo('OtherScientificTerm', 'Appear-in',model=AppearIn)

class Metric(BaseEntity):
    metric_usedFor = neomodel.RelationshipTo('Metric', 'Used-for',model=UsedFor)
    metric_partOf = neomodel.RelationshipTo('Metric', 'Part-of',model=PartOf)
    metric_featureOf = neomodel.RelationshipTo('Metric', 'Feature-of',model=FeatureOf)
    metric_compare = neomodel.RelationshipTo('Metric', 'Compare',model=Compare)
    metric_hyponymOf = neomodel.RelationshipTo('Metric', 'Hyponym-of',model=HyponymOf)
    metric_evaluateFor = neomodel.RelationshipTo('Metric', 'Evaluate-for',model=EvaluateFor)
    # metric_referTo = neomodel.RelationshipTo('Metric', 'Refer-to',model=ReferTo)
    metric_isA = neomodel.RelationshipTo('Metric', 'Is-a',model=IsA)
    metric_appearIn = neomodel.RelationshipTo('Metric', 'Appear-in',model=AppearIn)

class Generic(BaseEntity):
    generic_usedFor = neomodel.RelationshipTo('Generic', 'Used-for',model=UsedFor)
    generic_partOf = neomodel.RelationshipTo('Generic', 'Part-of',model=PartOf)
    generic_featureOf = neomodel.RelationshipTo('Generic', 'Feature-of',model=FeatureOf)
    generic_compare = neomodel.RelationshipTo('Generic', 'Compare',model=Compare)
    generic_hyponymOf = neomodel.RelationshipTo('Generic', 'Hyponym-of',model=HyponymOf)
    generic_evaluateFor = neomodel.RelationshipTo('Generic', 'Evaluate-for',model=EvaluateFor)
    # generic_referTo = neomodel.RelationshipTo('Generic', 'Refer-to',model=ReferTo)
    generic_isA = neomodel.RelationshipTo('Generic', 'Is-a',model=IsA)
    generic_appearIn = neomodel.RelationshipTo('Generic', 'Appear-in',model=AppearIn)

class Abbreviation(BaseEntity):
    abbreviation_referTo = neomodel.RelationshipTo('Abbreviation', 'Refer-to',model=ReferTo)
    abbreviation_isA = neomodel.RelationshipTo('Abbreviation', 'Is-a',model=IsA)


class Paper(BaseEntity):
    paper_isA = neomodel.RelationshipTo('Paper', 'Is-a',model=IsA)
    

class BaseRelation(neomodel.StructuredRel):
    # properties
    weight = FloatProperty(default=0)
    create_at = DateTimeProperty(
        default=datetime.now() # no specific timezone 
    )

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

class IsA(BaseRelation):
    pass

class AppearIn(BaseRelation):
    pass