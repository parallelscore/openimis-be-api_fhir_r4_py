from django.utils.translation import gettext
from insuree.models import Insuree, Gender, Education, Profession,Family
from api_fhir_r4.converters import BaseFHIRConverter
from api_fhir_r4.exceptions import FHIRRequestProcessException
from api_fhir_r4.models import HumanName, NameUse, ContactPointSystem, ContactPointUse,Member


class GroupConverterMixin(object):
    
    @classmethod
    def build_fhir_names_for_person(cls, person_obj):
        if not hasattr(person_obj, 'last_name') and not hasattr(person_obj, 'other_names'):
            raise FHIRRequestProcessException([gettext('Missing `last_name` and `other_names` for IMIS object')])
        head = HumanName()
        head.use = NameUse.USUAL.value
        head.family = person_obj.last_name
        head.given = [person_obj.other_names]
        return head
    
    @classmethod
    def build_fhir_members(cls,family_id):
        members =[]
        for insuree in Insuree.objects.filter(family__uuid=family_id):
            member = Member()
            member.inactive = False
            member.entity={
            "reference":"Patient"+'/'+insuree.uuid
            }
            members.append(member)
        return members
    
    @classmethod
    def build_fhir_location(cls,fhir_family, imis_family):
        locations ={}
        if imis_family.location is not None:
            locations['reference'] = 'Location'+'/'+imis_family.location.uuid
        fhir_family.location=locations
    