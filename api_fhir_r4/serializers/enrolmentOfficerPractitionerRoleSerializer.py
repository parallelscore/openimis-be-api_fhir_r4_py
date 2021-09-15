from core.models import Officer
from django.utils.translation import gettext

from api_fhir_r4.converters import EnrolmentOfficerPractitionerRoleConverter
from api_fhir_r4.exceptions import FHIRRequestProcessException
from api_fhir_r4.serializers import BaseFHIRSerializer


class EnrolmentOfficerPractitionerRoleSerializer(BaseFHIRSerializer):

    fhirConverter = EnrolmentOfficerPractitionerRoleConverter()
