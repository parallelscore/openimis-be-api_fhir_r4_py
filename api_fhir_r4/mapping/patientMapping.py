from insuree.models import Profession, Education, IdentificationType


class RelationshipMapping(object):

    relationship = {
        "1": "Brother/Sister",
        "2": "Father/Mother",
        "3": "Uncle/Aunt",
        "4": "Son/Daughter",
        "5": "Grand parents",
        "6": "Employee",
        "7": "Others",
        "8": "Spouse",
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
