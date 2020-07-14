from api_fhir_r4.converters import ClaimResponseConverter
from api_fhir_r4.serializers import BaseFHIRSerializer


class ClaimResponseSerializer(BaseFHIRSerializer):

    fhirConverter = ClaimResponseConverter
