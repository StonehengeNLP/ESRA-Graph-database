import neomodel

class BaseEntity(neomodel.StructuredNode):
    # id = neomodel.StringProperty(unique_index=True)
    # name = neomodel.StringProperty()
    # author = neomodel.RelationshipTo('Author', 'AUTHOR')
    pass

class Task(BaseEntity):
    name = neomodel.StringProperty(unique_index=True)
    method = neomodel.RelationshipFrom('Method', 'Used-for')
    task = neomodel.RelationshipFrom('Method', 'Used-for')

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
# work = RelationshipTo("Company", 'WORKS_AT', model=WorkRel)
