from api_fhir_r4.models import BackboneElement, DomainResource, Property,Element


class Characteristic(BackboneElement):
    type = Property('type', 'CodeableConcept', required=True)
    period = Property('period', 'Period')
    code = Property('code', 'CodeableConcept')
    valueCodeableConcept = Property('valueCodeableConcept', 'CodeableConcept')
    exclude = Property('exclude', bool)
    valueQuantity = Property("valueQuantity","Quantity")
    valueBoolean=Property('valueBoolean', bool)
    valueRange = Property('valueRange','Range')
    valueReference = Property('valueReference','Reference')

class GroupLocation(Element):
    name = Property('name',str)
    code=Property('code',str)
    
class Group(DomainResource):
    identifier = Property('identifier', 'Identifier', count_max='*')
    actual = Property('actual', bool)
    active = Property('active', bool)
    type = Property('type',str)
    inactive = Property('active', bool)
    code = Property('code', 'CodeableConcept')
    name = Property('name',str)
    quantity= Property('quantity',int)
    managingEntity = Property('managingEntity',str)
    member = Property('member','Member',count_max='*')
    characteristic = Property('characteristic','Characteristic',count_max='*')
    address = Property('address', 'Address', count_max='*')
    location = Property('location','GroupLocation')