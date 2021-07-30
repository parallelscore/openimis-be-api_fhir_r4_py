from insuree.models import Profession, Education, IdentificationType, Relation


class RelationshipMapping(object):

    relationship = {
        str(relation.id): relation.relation for relation in Relation.objects.all()
    }


class EducationLevelMapping(object):

    education_level = {
        str(education.id): education.education for education in Education.objects.all()
    }


class PatientProfessionMapping(object):

    patient_profession = {
        str(profession.id): profession.profession for profession in Profession.objects.all()
    }


class IdentificationTypeMapping(object):

    identification_type = {
        identification.code: identification.identification_type for identification in IdentificationType.objects.all()
    }


class MaritalStatusMapping(object):

    marital_status = {
        "M": "Married",
        "S": "Single",
        "D": "Divorced",
        "W": "Widowed",
        "UNK": "unknown"
    }
