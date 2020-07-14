from api_fhir_r4.converters.coverageConventer import CoverageConventer
from api_fhir_r4.serializers import BaseFHIRSerializer


class CoverageSerializer(BaseFHIRSerializer):

    fhirConverter = CoverageConventer
