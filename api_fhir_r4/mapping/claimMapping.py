from api_fhir_r4.configurations import R4ClaimConfig, GeneralConfiguration
from urllib.parse import urljoin


class ClaimPriorityMapping:
    SYSTEM = 'http://terminology.hl7.org/CodeSystem/processpriority'

    fhir_priority_coding = {
        'normal': {
            'system': SYSTEM,
            'code': 'normal',
            'display': 'Normal',
        }
    }


class ClaimVisitTypeMapping:
    SYSTEM = urljoin(GeneralConfiguration.get_system_base_url(), R4ClaimConfig.get_fhir_claim_visit_type_system())

    fhir_claim_visit_type_coding = {
        'E': {
            'system': SYSTEM,
            'code': 'E',
            'display': 'Emergency',
        },
        'R': {
            'system': SYSTEM,
            'code': 'R',
            'display': 'Referrals',
        },
        'O': {
            'system': SYSTEM,
            'code': 'O',
            'display': 'Other',
        }
    }


class ClaimItemCategoryMapping:
    SYSTEM = urljoin(GeneralConfiguration.get_system_base_url(), R4ClaimConfig.get_fhir_claim_item_category_system())

    fhir_claim_item_type_coding = {
        R4ClaimConfig.get_fhir_claim_item_code(): {
            'system': SYSTEM,
            'code': R4ClaimConfig.get_fhir_claim_item_code(),
            'display': 'Item',
        },
        R4ClaimConfig.get_fhir_claim_service_code(): {
            'system': SYSTEM,
            'code': R4ClaimConfig.get_fhir_claim_service_code(),
            'display': 'Service',
        }
    }
