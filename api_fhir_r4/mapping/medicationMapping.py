from api_fhir_r4.configurations import GeneralConfiguration


class ItemTypeMapping(object):

    item_type = {
        "D": "Drug",
        "M": "Medical_Consumable",
    }


class ItemVenueTypeMapping(object):

    item_venue_type = {
        "AMB": "ambulatory",
        "IMP": "IMP",
        "B": "both",
    }

    venue_fhir_imis = {
        "AMB": "O",
        "IMP": "I",
    }


class PatientCategoryMapping(object):
    GENDER_SYSTEM = "http://hl7.org/fhir/administrative-gender"
    AGE_SYSTEM = f"{GeneralConfiguration.get_system_base_url()}CodeSystem/usage-context-age-type"

    fhir_patient_category_coding = {
        "male": {
            "system": GENDER_SYSTEM,
            "code": "male",
            "display": "Male",
        },
        "female": {
            "system": GENDER_SYSTEM,
            "code": "female",
            "display": "Female",
        },
        "adult": {
            "system": AGE_SYSTEM,
            "code": "adult",
            "display": "Adult",
        },
        "child": {
            "system": AGE_SYSTEM,
            "code": "child",
            "display": "Child",
        },
    }

    imis_patient_category_flags = {
        "male": 1,
        "female": 2,
        "adult": 4,
        "child": 8,
    }
