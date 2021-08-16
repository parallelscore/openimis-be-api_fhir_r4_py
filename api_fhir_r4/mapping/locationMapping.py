from api_fhir_r4.configurations import R4LocationConfig
from api_fhir_r4.models.imisModelEnums import ImisLocationType


class LocationTypeMapping:
    SYSTEM = 'https://openimis.github.io/openimis_fhir_r4_ig/StructureDefinition/openimis-location'
    PHYSICAL_TYPE_SYSTEM = 'https://openimis.github.io/openimis_fhir_r4_ig/CodeSystem/location-type'

    PHYSICAL_TYPES_DEFINITIONS = {
        ImisLocationType.REGION.value: {
            'code': R4LocationConfig.get_fhir_code_for_region(),
            'display': 'Region',
            'system': PHYSICAL_TYPE_SYSTEM
        },
        ImisLocationType.DISTRICT.value: {
            'code': R4LocationConfig.get_fhir_code_for_district(),
            'display': 'District',
            'system': PHYSICAL_TYPE_SYSTEM
        },
        ImisLocationType.WARD.value: {
            'code': R4LocationConfig.get_fhir_code_for_ward(),
            'display': 'Municipality/Ward',
            'system': PHYSICAL_TYPE_SYSTEM
        },
        ImisLocationType.VILLAGE.value: {
            'code': R4LocationConfig.get_fhir_code_for_village(),
            'display': 'Village',
            'system': PHYSICAL_TYPE_SYSTEM
        }
    }