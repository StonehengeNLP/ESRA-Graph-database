import neomodel

class BaseEntity(neomodel.StructuredNode):
    name = neomodel.StringProperty(unique_index=True)

    #relation from Task to ...
    task_usedFor = neomodel.RelationshipFrom('Task', 'Used-for')
    task_partOf = neomodel.RelationshipFrom('Task', 'Part-of')
    task_featureOf = neomodel.RelationshipFrom('Task', 'Feature-of')
    task_compare = neomodel.RelationshipFrom('Task', 'Compare')
    task_hyponymOf = neomodel.RelationshipFrom('Task', 'Hyponym-of')
    task_evaluateFor = neomodel.RelationshipFrom('Task', 'Evaluate-for')
    task_referTo = neomodel.RelationshipFrom('Task', 'Refer-to')
    task_isA = neomodel.RelationshipFrom('Task', 'Is-a')
    task_appearIn = neomodel.RelationshipFrom('Task', 'Appear-in')

    #relation from Method to ...
    method_usedFor = neomodel.RelationshipFrom('Method', 'Used-for')
    method_partOf = neomodel.RelationshipFrom('Method', 'Part-of')
    method_featureOf = neomodel.RelationshipFrom('Method', 'Feature-of')
    method_compare = neomodel.RelationshipFrom('Method', 'Compare')
    method_hyponymOf = neomodel.RelationshipFrom('Method', 'Hyponym-of')
    method_evaluateFor = neomodel.RelationshipFrom('Method', 'Evaluate-for')
    method_referTo = neomodel.RelationshipFrom('Method', 'Refer-to')
    method_isA = neomodel.RelationshipFrom('Method', 'Is-a')
    method_appearIn = neomodel.RelationshipFrom('Method', 'Appear-in')

    #relation from Material to ... 
    material_usedFor = neomodel.RelationshipFrom('Material', 'Used-for')
    material_partOf = neomodel.RelationshipFrom('Material', 'Part-of')
    material_featureOf = neomodel.RelationshipFrom('Material', 'Feature-of')
    material_compare = neomodel.RelationshipFrom('Material', 'Compare')
    material_hyponymOf = neomodel.RelationshipFrom('Material', 'Hyponym-of')
    material_evaluateFor = neomodel.RelationshipFrom('Material', 'Evaluate-for')
    material_referTo = neomodel.RelationshipFrom('Material', 'Refer-to')
    material_isA = neomodel.RelationshipFrom('Material', 'Is-a')
    material_appearIn = neomodel.RelationshipFrom('Material', 'Appear-in')

    #relation from OtherScientificTerm to ... 
    otherScientificTerm_usedFor = neomodel.RelationshipFrom('OtherScientificTerm', 'Used-for')
    otherScientificTerm_partOf = neomodel.RelationshipFrom('OtherScientificTerm', 'Part-of')
    otherScientificTerm_featureOf = neomodel.RelationshipFrom('OtherScientificTerm', 'Feature-of')
    otherScientificTerm_compare = neomodel.RelationshipFrom('OtherScientificTerm', 'Compare')
    otherScientificTerm_hyponymOf = neomodel.RelationshipFrom('OtherScientificTerm', 'Hyponym-of')
    otherScientificTerm_evaluateFor = neomodel.RelationshipFrom('OtherScientificTerm', 'Evaluate-for')
    otherScientificTerm_referTo = neomodel.RelationshipFrom('OtherScientificTerm', 'Refer-to')
    otherScientificTerm_isA = neomodel.RelationshipFrom('OtherScientificTerm', 'Is-a')
    otherScientificTerm_appearIn = neomodel.RelationshipFrom('OtherScientificTerm', 'Appear-in')

    #relation from Metric to ... 
    metric_usedFor = neomodel.RelationshipFrom('Metric', 'Used-for')
    metric_partOf = neomodel.RelationshipFrom('Metric', 'Part-of')
    metric_featureOf = neomodel.RelationshipFrom('Metric', 'Feature-of')
    metric_compare = neomodel.RelationshipFrom('Metric', 'Compare')
    metric_hyponymOf = neomodel.RelationshipFrom('Metric', 'Hyponym-of')
    metric_evaluateFor = neomodel.RelationshipFrom('Metric', 'Evaluate-for')
    metric_referTo = neomodel.RelationshipFrom('Metric', 'Refer-to')
    metric_isA = neomodel.RelationshipFrom('Metric', 'Is-a')
    metric_appearIn = neomodel.RelationshipFrom('Metric', 'Appear-in')

    #relation from Generic to ... 
    generic_usedFor = neomodel.RelationshipFrom('Generic', 'Used-for')
    generic_partOf = neomodel.RelationshipFrom('Generic', 'Part-of')
    generic_featureOf = neomodel.RelationshipFrom('Generic', 'Feature-of')
    generic_compare = neomodel.RelationshipFrom('Generic', 'Compare')
    generic_hyponymOf = neomodel.RelationshipFrom('Generic', 'Hyponym-of')
    generic_evaluateFor = neomodel.RelationshipFrom('Generic', 'Evaluate-for')
    generic_referTo = neomodel.RelationshipFrom('Generic', 'Refer-to')
    generic_isA = neomodel.RelationshipFrom('Generic', 'Is-a')
    generic_appearIn = neomodel.RelationshipFrom('Generic', 'Appear-in')

    #relation from Abbreviation to ... 
    abbreviation_usedFor = neomodel.RelationshipFrom('Abbreviation', 'Used-for')
    abbreviation_partOf = neomodel.RelationshipFrom('Abbreviation', 'Part-of')
    abbreviation_featureOf = neomodel.RelationshipFrom('Abbreviation', 'Feature-of')
    abbreviation_compare = neomodel.RelationshipFrom('Abbreviation', 'Compare')
    abbreviation_hyponymOf = neomodel.RelationshipFrom('Abbreviation', 'Hyponym-of')
    abbreviation_evaluateFor = neomodel.RelationshipFrom('Abbreviation', 'Evaluate-for')
    abbreviation_referTo = neomodel.RelationshipFrom('Abbreviation', 'Refer-to')
    abbreviation_isA = neomodel.RelationshipFrom('Abbreviation', 'Is-a')
    abbreviation_appearIn = neomodel.RelationshipFrom('Abbreviation', 'Appear-in')

    #relation from Paper to ... 
    paper_usedFor = neomodel.RelationshipFrom('Paper', 'Used-for')
    paper_partOf = neomodel.RelationshipFrom('Paper', 'Part-of')
    paper_featureOf = neomodel.RelationshipFrom('Paper', 'Feature-of')
    paper_compare = neomodel.RelationshipFrom('Paper', 'Compare')
    paper_hyponymOf = neomodel.RelationshipFrom('Paper', 'Hyponym-of')
    paper_evaluateFor = neomodel.RelationshipFrom('Paper', 'Evaluate-for')
    paper_referTo = neomodel.RelationshipFrom('Paper', 'Refer-to')
    paper_isA = neomodel.RelationshipFrom('Paper', 'Is-a')
    paper_appearIn = neomodel.RelationshipFrom('Paper', 'Appear-in')
    
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

class Generic(BaseEntity):
    pass

class Abbreviation(BaseEntity):
    pass

class Paper(BaseEntity):
    pass

class BaseRelation(neomodel.StructuredRel):
    # uid = StringProperty(unique=True)
    # start_date = DateTimeProperty()
    # end_date = DateTimeProperty()
    # position = StringProperty() 
    pass

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
