from api_fhir_r4.configurations import R4LocationConfig
from api_fhir_r4.models.imisModelEnums import ImisLocationType, ContactPointSystem


class HealthFacilityOrganizationTypeMapping:
    LEGAL_FORM_CODE = 'D'
    LEGAL_FORM_DISPLAY = 'District organization'
    LEGAL_FORM_SYSTEM = 'https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/organization-legal-form'
    LEGAL_FORM_URL = 'https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/organization-legal-form'

    ORGANIZATION_TYPE = 'prov'

    EMAIL_CONTACT_POINT_SYSTEM = ContactPointSystem.EMAIL
    PHONE_CONTACT_POINT_SYSTEM = ContactPointSystem.PHONE
    FAX_CONTACT_POINT_SYSTEM = ContactPointSystem.FAX

    ADDRESS_LOCATION_REFERENCE_URL = \
        'https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/address-location-reference'

    CONTRACT_PURPOSE = {
        'code': 'PAYOR',
        'system': 'http://terminology.hl7.org/CodeSystem/contactentity-type'
    }

    LEVEL_DISPLAY_MAPPING = {
        'D': 'Dispensary',
        'C': 'Health Centre',
        'H': 'Hospital'
    }

    LEVEL_SYSTEM = 'https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/organization-hf-level'
