import neomodel

class BaseEntity(neomodel.StructuredNode):
    # id = neomodel.StringProperty(unique_index=True)
    # name = neomodel.StringProperty()
    # author = neomodel.RelationshipTo('Author', 'AUTHOR')
    pass

class Task(BaseEntity):
    name = neomodel.StringProperty(unique_index=True)
    
    # method = neomodel.RelationshipFrom('Method', 'Used-for')
    # task = neomodel.RelationshipFrom('Task', 'Used-for')

    #variable name : <from>_<relationType>

    #relation from task to task
    task_partOf = neomodel.RelationshipFrom('Task', 'Part-of')
    task_compare = neomodel.RelationshipFrom('Task', 'Compare')
    task_HyponymOf = neomodel.RelationshipFrom('Task', 'Hyponym-of')
    # concept : task = task_partOf + task_compare + task_HyponymOf 

    #relation from method to task
    method_usedFor = neomodel.RelationshipFrom('Method', 'Used-for')

    #relation from material to task
    material_usedFor = neomodel.RelationshipFrom('Material', 'Used-for')
    material_evauateFor = neomodel.RelationshipFrom('Material', 'Evaluate-for')

    #relation from OtherscientificTerm to task
    otherScientificTerm_hyponymOf = neomodel.RelationshipFrom('OtherSientificTerm', 'Hyponym-of')
    otherScientificTerm_usedFor = neomodel.RelationshipFrom('OtherSientificTerm', 'Used-for')

    #relation from metric to task
    metric_evaluateFor = neomodel.RelationshipFrom('Metric', 'Evaluate-for')

    #relation from generic to task
    generic_usedFor = neomodel.RelationshipFrom('Generic', 'Used-for')
    generic_compare = neomodel.RelationshipFrom('Generic', 'Compare')




class Method(BaseEntity):
    name = neomodel.StringProperty(unique_index=True)
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
# work = RelationshipTo("Company", 'WORKS_AT', model=WorkRel)
