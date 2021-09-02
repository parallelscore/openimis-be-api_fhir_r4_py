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
