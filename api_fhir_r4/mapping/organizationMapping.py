from urllib.parse import urljoin

from api_fhir_r4.configurations import GeneralConfiguration, R4OrganisationConfig
from api_fhir_r4.models.imisModelEnums import ContactPointSystem


class HealthFacilityOrganizationTypeMapping:
    LEGAL_FORM_CODE = 'D'
    LEGAL_FORM_DISPLAY = 'District organization'
    LEGAL_FORM_SYSTEM = 'CodeSystem/organization-legal-form'
    LEGAL_FORM_URL = f'{GeneralConfiguration.get_system_base_url()}StructureDefinition/organization-legal-form'

    ORGANIZATION_TYPE = 'prov'

    EMAIL_CONTACT_POINT_SYSTEM = ContactPointSystem.EMAIL
    PHONE_CONTACT_POINT_SYSTEM = ContactPointSystem.PHONE
    FAX_CONTACT_POINT_SYSTEM = ContactPointSystem.FAX

    ADDRESS_LOCATION_REFERENCE_URL = \
        f'{GeneralConfiguration.get_system_base_url()}/StructureDefinition/address-location-reference'

    CONTRACT_PURPOSE = {
        'code': 'PAYOR',
        'system': 'http://terminology.hl7.org/CodeSystem/contactentity-type'
    }

    LEVEL_DISPLAY_MAPPING = {
        'D': 'Dispensary',
        'C': 'Health Centre',
        'H': 'Hospital'
    }

    LEVEL_SYSTEM = f'{GeneralConfiguration.get_system_base_url()}/CodeSystem/organization-hf-level'


class PolicyHolderOrganisationLegalFormMapping(object):
    SYSTEM = urljoin(GeneralConfiguration.get_system_base_url(),
                     R4OrganisationConfig.get_fhir_ph_organisation_legal_form_code_system())

    fhir_ph_organisation_legal_form = {
        1: {
            "system": SYSTEM,
            "code": "1",
            "display": "Personal Company",
        },
        2: {
            "system": SYSTEM,
            "code": "2",
            "display": "Limited Risk Company",
        },
        3: {
            "system": SYSTEM,
            "code": "3",
            "display": "Association",
        },
        4: {
            "system": SYSTEM,
            "code": "4",
            "display": "Government",
        },
        5: {
            "system": SYSTEM,
            "code": "5",
            "display": "Union",
        },
    }


class PolicyHolderOrganisationActivityMapping(object):
    SYSTEM = urljoin(GeneralConfiguration.get_system_base_url(),
                     R4OrganisationConfig.get_fhir_ph_organisation_activity_code_system())

    fhir_ph_organisation_activity = {
        1: {
            "system": SYSTEM,
            "code": "1",
            "display": "Retail",
        },
        2: {
            "system": SYSTEM,
            "code": "2",
            "display": "Industry",
        },
        3: {
            "system": SYSTEM,
            "code": "3",
            "display": "Building",
        },
        4: {
            "system": SYSTEM,
            "code": "4",
            "display": "Sailing",
        },
        5: {
            "system": SYSTEM,
            "code": "5",
            "display": "Services",
        },
    }
