from api_fhir_r4.converters import InsurancePlanConverter
from api_fhir_r4.serializers import BaseFHIRSerializer


class InsurancePlanSerializer(BaseFHIRSerializer):
    fhirConverter = InsurancePlanConverter()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
