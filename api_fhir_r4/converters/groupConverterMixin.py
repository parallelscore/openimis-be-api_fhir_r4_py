from django.utils.translation import gettext
from insuree.models import Insuree
from api_fhir_r4.exceptions import FHIRRequestProcessException
from fhir.resources.humanname import HumanName
from fhir.resources.group import GroupMember


class GroupConverterMixin(object):
    
    @classmethod
    def build_fhir_names_for_person(cls, person_obj):
        if not hasattr(person_obj, 'last_name') and not hasattr(person_obj, 'other_names'):
            raise FHIRRequestProcessException([gettext('Missing `last_name` and `other_names` for IMIS object')])
        head = HumanName.construct()
        head.use = "usual"
        head.family = person_obj.last_name
        head.given = [person_obj.other_names]
        return head

    @classmethod
    def build_fhir_members(cls, family_id):
        members = []
        for insuree in Insuree.objects.filter(family__uuid=family_id, validity_to__isnull=True):
            member = GroupMember.construct()
            member.entity = {
                "reference": f'Patient/{insuree.chf_id}',
                "type": "Patient",
            }
            members.append(member)
        return members
