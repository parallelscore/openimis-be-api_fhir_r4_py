from api_fhir_r4.converters import HealthFacilityOrganisationConverter
from api_fhir_r4.serializers import BaseFHIRSerializer
from location.models import HealthFacility


class HealthFacilityOrganisationSerializer(BaseFHIRSerializer):
    fhirConverter = HealthFacilityOrganisationConverter()

    def create(self, validated_data):
        raise NotImplementedError('Health Facility should be created using Practitioner resource.')

    def update(self, instance, validated_data):
        raise NotImplementedError('Health Facility should be updated using Practitioner resource.')
