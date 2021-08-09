import os
import urllib
from urllib.parse import urlparse

from django.utils.translation import gettext
from insuree.models import Insuree, Gender, Education, Profession, Family, \
    InsureePhoto, Relation, IdentificationType
from location.models import Location
from api_fhir_r4.configurations import R4IdentifierConfig, GeneralConfiguration, R4MaritalConfig
from api_fhir_r4.converters import BaseFHIRConverter, PersonConverterMixin, ReferenceConverterMixin
from api_fhir_r4.converters.healthcareServiceConverter import HealthcareServiceConverter
from api_fhir_r4.converters.locationConverter import LocationConverter
from api_fhir_r4.mapping.patientMapping import RelationshipMapping, EducationLevelMapping, \
    PatientProfessionMapping, IdentificationTypeMapping, MaritalStatusMapping
from api_fhir_r4.models.imisModelEnums import ImisMaritalStatus
from fhir.resources.patient import Patient, PatientLink, PatientContact
from fhir.resources.extension import Extension
from fhir.resources.attachment import Attachment
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.identifier import Identifier
from api_fhir_r4.utils import TimeUtils, DbManagerUtils


class PatientConverter(BaseFHIRConverter, PersonConverterMixin, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_insuree, reference_type=ReferenceConverterMixin.UUID_REFERENCE_TYPE):
        fhir_patient = Patient.construct()
        cls.build_fhir_pk(fhir_patient, imis_insuree, reference_type)
        cls.build_human_names(fhir_patient, imis_insuree)
        cls.build_fhir_identifiers(fhir_patient, imis_insuree)
        cls.build_fhir_birth_date(fhir_patient, imis_insuree)
        cls.build_fhir_gender(fhir_patient, imis_insuree)
        cls.build_fhir_marital_status(fhir_patient, imis_insuree)
        cls.build_fhir_telecom(fhir_patient, imis_insuree)
        cls.build_fhir_addresses(fhir_patient, imis_insuree)
        cls.build_fhir_extentions(fhir_patient, imis_insuree, reference_type)
        cls.build_fhir_contact(fhir_patient, imis_insuree)
        cls.build_fhir_photo(fhir_patient, imis_insuree)
        cls.build_fhir_general_practitioner(fhir_patient, imis_insuree)
        return fhir_patient

    @classmethod
    def to_imis_obj(cls, fhir_patient, audit_user_id):
        errors = []
        fhir_patient = Patient(**fhir_patient)
        imis_insuree = cls.createDefaultInsuree(audit_user_id)
        cls.build_imis_names(imis_insuree, fhir_patient, errors)
        cls.build_imis_identifiers(imis_insuree, fhir_patient)
        cls.build_imis_birth_date(imis_insuree, fhir_patient, errors)
        cls.build_imis_gender(imis_insuree, fhir_patient)
        cls.build_imis_marital(imis_insuree, fhir_patient)
        cls.build_imis_contacts(imis_insuree, fhir_patient)
        cls.build_imis_addresses(imis_insuree, fhir_patient)
        cls.build_imis_photo(imis_insuree, fhir_patient, errors)
        cls.build_imis_extentions(imis_insuree, fhir_patient, errors)
        cls.build_imis_family(imis_insuree, fhir_patient, errors)
        cls.build_imis_relationship(imis_insuree, fhir_patient)
        return imis_insuree

    @classmethod
    def build_fhir_pk(cls, fhir_patient, resource, reference_type: str = None):
        if reference_type == ReferenceConverterMixin.CODE_REFERENCE_TYPE:
            fhir_patient.id = resource.chf_id
        else:
            super().build_fhir_pk(fhir_patient, resource, reference_type)

    @classmethod
    def get_fhir_code_identifier_type(cls):
        return R4IdentifierConfig.get_fhir_chfid_type_code()

    @classmethod
    def get_reference_obj_uuid(cls, imis_patient: Insuree):
        return imis_patient.uuid

    @classmethod
    def get_reference_obj_id(cls, imis_patient: Insuree):
        return imis_patient.id

    @classmethod
    def get_reference_obj_code(cls, imis_patient: Insuree):
        return imis_patient.chf_id

    @classmethod
    def build_imis_extentions(cls, imis_insuree, fhir_patient, errors):
        for extension in fhir_patient.extension:
            if extension.url == f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-is-head":
                imis_insuree.head = extension.valueBoolean

            elif extension.url == f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-education-level":
                try:
                    imis_insuree.education = Education.objects.get(id=extension.valueCodeableConcept.coding[0].code)
                except:
                    imis_insuree.education = None

            elif extension.url == f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-profession":
                try:
                    imis_insuree.profession = Profession.objects.get(id=extension.valueCodeableConcept.coding[0].code)
                except:
                    imis_insuree.profession = None

            elif extension.url == f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-card-issued":
                try:
                    imis_insuree.card_issued = extension.valueBoolean
                except:
                    imis_insuree.card_issued = False

            elif extension.url == f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-identification":
                try:
                    for ext in extension.extension:
                        if ext.url == "number":
                            imis_insuree.passport = ext.valueString
                        if ext.url == "type":
                            imis_insuree.type_of_id = IdentificationType.objects.get(code=ext.valueCodeableConcept.coding[0].code)
                except:
                    imis_insuree.passport = None
                    imis_insuree.type_of_id = None
            else:
                pass
    
    @classmethod
    def get_location_reference(cls,location):
      return location.rsplit('/',1)[1]

    @classmethod
    def get_fhir_resource_type(cls):
        return Patient

    @classmethod
    def get_imis_obj_by_fhir_reference(cls, reference, errors=None):
        imis_insuree_uuid = cls.get_resource_id_from_reference(reference)
        return DbManagerUtils.get_object_or_none(Insuree, uuid=imis_insuree_uuid)

    @classmethod
    def createDefaultInsuree(cls, audit_user_id):
        imis_insuree = Insuree()
        # temporary set uuid as None - this will be generated in service create insuree from that module
        imis_insuree.uuid = None
        imis_insuree.head = GeneralConfiguration.get_default_value_of_patient_head_attribute()
        imis_insuree.card_issued = GeneralConfiguration.get_default_value_of_patient_card_issued_attribute()
        imis_insuree.validity_from = TimeUtils.now()
        imis_insuree.audit_user_id = audit_user_id
        return imis_insuree

    @classmethod
    def build_human_names(cls, fhir_patient, imis_insuree):
        name = cls.build_fhir_names_for_person(imis_insuree)
        if type(fhir_patient.name) is not list:
            fhir_patient.name = [name]
        else:
            fhir_patient.name.append(name)

    @classmethod
    def build_imis_names(cls, imis_insuree, fhir_patient, errors):
        names = fhir_patient.name
        if not cls.valid_condition(names is None, gettext('Missing patient `name` attribute'), errors):
            imis_insuree.last_name, imis_insuree.other_names = cls.build_imis_last_and_other_name(names)
            cls.valid_condition(imis_insuree.last_name is None, gettext('Missing patient family name'), errors)
            cls.valid_condition(imis_insuree.other_names is None, gettext('Missing patient given name'), errors)

    @classmethod
    def build_fhir_identifiers(cls, fhir_patient, imis_insuree):
        identifiers = []
        cls.build_all_identifiers(identifiers, imis_insuree)
        cls.build_fhir_passport_identifier(identifiers, imis_insuree)
        fhir_patient.identifier = identifiers

    @classmethod
    def build_fhir_code_identifier(cls, identifiers, imis_object: Insuree):
        # Patient don't have code so chfid is used instead as code identifier
        if hasattr(imis_object, 'chf_id'):
            identifiers.append(cls.__build_chfid_identifier(imis_object.chf_id))

    @classmethod
    def __build_chfid_identifier(cls, chfid):
        return cls.build_fhir_identifier(chfid,
                                         R4IdentifierConfig.get_fhir_identifier_type_system(),
                                         R4IdentifierConfig.get_fhir_chfid_type_code())

    @classmethod
    def build_imis_identifiers(cls, imis_insuree, fhir_patient):
        value = cls.get_fhir_identifier_by_code(fhir_patient.identifier,
                                                R4IdentifierConfig.get_fhir_chfid_type_code())
        if value:
            imis_insuree.chf_id = value
        value = cls.get_fhir_identifier_by_code(fhir_patient.identifier,
                                                R4IdentifierConfig.get_fhir_passport_type_code())
        if value:
            imis_insuree.passport = value

    @classmethod
    def build_fhir_chfid_identifier(cls, identifiers, imis_insuree):
        if imis_insuree.chf_id:
            identifier = cls.build_fhir_identifier(imis_insuree.chf_id,
                                                   R4IdentifierConfig.get_fhir_identifier_type_system(),
                                                   R4IdentifierConfig.get_fhir_chfid_type_code())
            identifiers.append(identifier)

    @classmethod
    def build_fhir_passport_identifier(cls, identifiers, imis_insuree):
        if hasattr(imis_insuree, "type_of_id") and imis_insuree.type_of_id is not None:
            pass  # TODO typeofid isn't provided, this section should contain logic used to create passport field based on typeofid
        elif imis_insuree.passport:
            identifier = cls.build_fhir_identifier(imis_insuree.passport,
                                                   R4IdentifierConfig.get_fhir_identifier_type_system(),
                                                   R4IdentifierConfig.get_fhir_passport_type_code())
            identifiers.append(identifier)

    @classmethod
    def build_fhir_birth_date(cls, fhir_patient, imis_insuree):
        from core import datetime
        # check if datetime object
        if isinstance(imis_insuree.dob, datetime.datetime):
            fhir_patient.birthDate = str(imis_insuree.dob.date().isoformat())
        else:
            fhir_patient.birthDate = str(imis_insuree.dob.isoformat())
        
    @classmethod
    def build_imis_family(cls, imis_insuree, fhir_patient, errors):
        # get chfid
        family_reference = None
        if fhir_patient.extension:
            for extension in fhir_patient.extension:
                if "/StructureDefinition/patient-group-reference" in extension.url:
                    family_reference = extension.valueReference.reference
        if family_reference:
            if imis_insuree.head:
                for extension in  fhir_patient.extension:
                    if "StructureDefinition/address-location-reference" in extension.url:
                        value = cls.get_location_reference(extension.valueReference.reference)
                        if value:
                            try:
                                # split 'viilage'
                                value = value.split('-')[0]
                                imis_insuree.current_village = Location.objects.get(name=value)
                            except:
                                imis_insuree.current_village = False
            else:
                try:
                    # split family reference
                    family_reference = family_reference.split('/')[1]
                    family_reference = family_reference.split('-')[0]
                    imis_insuree.family = Family.objects.get(head_insuree__last_name=family_reference, validity_to__isnull=True)
                except Exception as e:
                    raise e

    @classmethod
    def build_imis_link(cls, imis_insuree,fhir_link):
        patient = fhir_link[0].other.reference
        value = patient.rsplit('/',1)[1]
        return value
    
    @classmethod
    def build_imis_relationship(cls, imis_insuree,fhir_patient):
        if fhir_patient.contact:
            for contact in fhir_patient.contact:
                if contact.relationship:
                    relationship_name = None
                    for relationship in contact.relationship:
                        for coding in relationship.coding:
                            if "CodeSystem/patient-contact-relationship" in coding.system:
                                relationship_name = coding.display
                    try:
                        relation = Relation.objects.get(relation=relationship_name)
                        imis_insuree.relationship = relation
                    except:
                        pass
    
    @classmethod
    def build_imis_birth_date(cls, imis_insuree, fhir_patient, errors):
        birth_date = fhir_patient.birthDate
        if not cls.valid_condition(birth_date is None, gettext('Missing patient `birthDate` attribute'), errors):
            imis_insuree.dob = TimeUtils.str_to_date(birth_date)

    @classmethod
    def build_fhir_gender(cls, fhir_patient, imis_insuree):
        if imis_insuree.gender:
            code = imis_insuree.gender.code
            if code == GeneralConfiguration.get_male_gender_code():
                fhir_patient.gender = "male"
            elif code == GeneralConfiguration.get_female_gender_code():
                fhir_patient.gender = "female"
            elif code == GeneralConfiguration.get_other_gender_code():
                fhir_patient.gender = "other"
        else:
            fhir_patient.gender = "unknown"

    @classmethod
    def build_imis_gender(cls, imis_insuree, fhir_patient):
        gender = fhir_patient.gender
    
        if gender is not None:
            imis_gender_code = None
            if gender == GeneralConfiguration.get_male_gender_code():
                imis_gender_code = "M"
            elif gender == GeneralConfiguration.get_female_gender_code():
                imis_gender_code = "F"
            elif gender == GeneralConfiguration.get_other_gender_code():
                imis_gender_code = "O"
            if imis_gender_code is not None:
                imis_insuree.gender = Gender.objects.get(pk=imis_gender_code)

    @classmethod
    def build_fhir_marital_status(cls, fhir_patient, imis_insuree):
        if imis_insuree.marital:
            display = MaritalStatusMapping.marital_status[imis_insuree.marital]
            fhir_patient.maritalStatus = \
                cls.build_codeable_concept(code=imis_insuree.marital,
                                           system=R4MaritalConfig.get_fhir_marital_status_system())
            if len(fhir_patient.maritalStatus.coding) == 1:
                fhir_patient.maritalStatus.coding[0].display = display

    @classmethod
    def build_imis_marital(cls, imis_insuree, fhir_patient):
        marital_status = fhir_patient.maritalStatus
        if marital_status is not None:
            for maritialCoding in marital_status.coding:
                if maritialCoding.system == R4MaritalConfig.get_fhir_marital_status_system():
                    code = maritialCoding.code
                    if code == R4MaritalConfig.get_fhir_married_code():
                        imis_insuree.marital = ImisMaritalStatus.MARRIED.value
                    elif code == R4MaritalConfig.get_fhir_never_married_code():
                        imis_insuree.marital = ImisMaritalStatus.SINGLE.value
                    elif code == R4MaritalConfig.get_fhir_divorced_code():
                        imis_insuree.marital = ImisMaritalStatus.DIVORCED.value
                    elif code == R4MaritalConfig.get_fhir_widowed_code():
                        imis_insuree.marital = ImisMaritalStatus.WIDOWED.value
                    elif code == R4MaritalConfig.get_fhir_unknown_marital_status_code():
                        imis_insuree.marital = ImisMaritalStatus.NOT_SPECIFIED.value

    @classmethod
    def build_fhir_telecom(cls, fhir_patient, imis_insuree):
        fhir_patient.telecom = cls.build_fhir_telecom_for_person(phone=imis_insuree.phone, email=imis_insuree.email)

    @classmethod
    def build_imis_contacts(cls, imis_insuree, fhir_patient):
        imis_insuree.phone, imis_insuree.email = cls.build_imis_phone_num_and_email(fhir_patient.telecom)

    @classmethod
    def build_fhir_addresses(cls, fhir_patient, imis_insuree):
        addresses = []
        # family slice - required
        if imis_insuree.family is not None:
            imis_family = imis_insuree.family
            family_address = cls.build_fhir_address(imis_family.address, "home", "physical")
            if imis_family.location:
                family_address.state = imis_family.location.parent.parent.parent.name
                family_address.district = imis_family.location.parent.parent.name

                # municipality extension
                extension = Extension.construct()
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/address-municipality"
                extension.valueString = imis_family.location.parent.name
                family_address.extension = [extension]

                # address location reference extension
                extension = Extension.construct()
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/address-location-reference"
                reference_location = Reference.construct()
                reference_location.reference = F"Location/{imis_family.location.name}-village"
                extension.valueReference = reference_location
                family_address.extension.append(extension)

                family_address.city = imis_family.location.name

            if family_address is not None:
                if type(addresses) is not list:
                    addresses = [family_address]
                else:
                    addresses.append(family_address)

        # insuree slice
        if imis_insuree.current_address:
            current_address = cls.build_fhir_address(imis_insuree.current_address, "temp", "physical")
            if imis_insuree.current_village:
                current_address.state = imis_insuree.current_village.parent.parent.parent.name
                current_address.district = imis_insuree.current_village.parent.parent.name

                # municipality extension
                extension = Extension.construct()
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/address-municipality"
                extension.valueString = imis_insuree.current_village.parent.name
                current_address.extension = [extension]

                # address location reference extension
                extension = Extension.construct()
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/address-location-reference"
                reference_location = Reference.construct()
                reference_location.reference = F"Location/{imis_insuree.current_village.name}-village"
                extension.valueReference = reference_location
                current_address.extension.append(extension)

                current_address.city = imis_insuree.current_village.name

            if imis_insuree.current_address is not None:
                if type(addresses) is not list:
                    addresses = [current_address]
                else:
                    addresses.append(current_address)
                    
        fhir_patient.address = addresses

    @classmethod
    def build_imis_addresses(cls, imis_insuree, fhir_patient):
        addresses = fhir_patient.address
        if addresses:
            for address in addresses:
                # insuree use temp address
                if address.use == "temp":
                    if address.type == "physical":
                        imis_insuree.current_address = address.text
                        for ext in address.extension:
                            if "StructureDefinition/address-location-reference" in ext.url:
                                value = cls.get_location_reference(ext.valueReference.reference)
                                if value:
                                    try:
                                        # split 'viilage'
                                        value = value.split('-')[0]
                                        imis_insuree.current_village = Location.objects.get(name=value)
                                    except:
                                        imis_insuree.current_village = False
                    elif address.type == "both":
                        imis_insuree.geolocation = address.text

    @classmethod
    def build_fhir_extentions(cls, fhir_patient, imis_insuree, reference_type):
        fhir_patient.extension = []

        def build_extension(fhir_patient, imis_insuree, value):
            extension = Extension.construct()
            if value == "head":
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-is-head"
                extension.valueBoolean = imis_insuree.head

            elif value == "education.education":
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-education-level"
                if hasattr(imis_insuree, "education") and imis_insuree.education is not None:
                    display = EducationLevelMapping.education_level[str(imis_insuree.education.id)]
                    system = f"{GeneralConfiguration.get_system_base_url()}CodeSystem/patient-education-level"
                    extension.valueCodeableConcept = cls.build_codeable_concept(code=str(imis_insuree.education.id), system=system)
                    if len(extension.valueCodeableConcept.coding) == 1:
                        extension.valueCodeableConcept.coding[0].display = display

            elif value == "patient.card.issue":
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-card-issued"
                extension.valueBoolean = imis_insuree.card_issued

            elif value == "patient.group.reference":
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-group-reference"
                reference_group = Reference.construct()
                reference_group.reference = F"Group/{imis_insuree.last_name}-family"
                extension.valueReference = reference_group

            elif value == "patient.identification":
                nested_extension = Extension.construct()
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-identification"
                if hasattr(imis_insuree, "type_of_id") and imis_insuree.type_of_id:
                    if hasattr(imis_insuree, "passport") and imis_insuree.passport:
                        # add number extension
                        nested_extension.url = "number"
                        nested_extension.valueString = imis_insuree.passport
                        extension.extension = [nested_extension]
                        # add identifier extension
                        nested_extension = Extension.construct()
                        nested_extension.url = "type"
                        system = f"{GeneralConfiguration.get_system_base_url()}CodeSystem/patient-identification-types"
                        nested_extension.valueCodeableConcept = cls.build_codeable_concept(code=imis_insuree.type_of_id.code, system=system)
                        extension.extension.append(nested_extension)

            else:
                extension.url = f"{GeneralConfiguration.get_system_base_url()}StructureDefinition/patient-profession"
                if hasattr(imis_insuree, "profession") and imis_insuree.profession is not None:
                    display = PatientProfessionMapping.patient_profession[str(imis_insuree.profession.id)]
                    system = f"{GeneralConfiguration.get_system_base_url()}CodeSystem/patient-profession"
                    extension.valueCodeableConcept = cls.build_codeable_concept(code=str(imis_insuree.profession.id), system=system)
                    if len(extension.valueCodeableConcept.coding) == 1:
                        extension.valueCodeableConcept.coding[0].display = display

            if type(fhir_patient.extension) is not list:
                fhir_patient.extension = [extension]
            else:
                fhir_patient.extension.append(extension)


        if imis_insuree.head is not None:
            build_extension(fhir_patient, imis_insuree, "head")
        if imis_insuree.education is not None:
            build_extension(fhir_patient, imis_insuree, "education.education")
        if imis_insuree.profession is not None:
            build_extension(fhir_patient, imis_insuree, "profession.profession")
        if imis_insuree.card_issued is not None:
            build_extension(fhir_patient, imis_insuree, "patient.card.issue")
        if imis_insuree.family is not None:
            build_extension(fhir_patient, imis_insuree, "patient.group.reference")
        if imis_insuree.type_of_id is not None and imis_insuree.passport is not None:
            build_extension(fhir_patient, imis_insuree, "patient.identification")

    @classmethod
    def build_fhir_contact(cls, fhir_patient, imis_insuree):
        fhir_contact = PatientContact.construct()
        if imis_insuree.relationship is not None and imis_insuree.family is not None \
                and imis_insuree.family.head_insuree is not None:
            system = f"{GeneralConfiguration.get_system_base_url()}CodeSystem/patient-contact-relationship"
            # map to the fhir value from imis one
            display = RelationshipMapping.relationship[str(imis_insuree.relationship.id)]
            fhir_contact.relationship = [cls.build_codeable_concept(code=imis_insuree.relationship.id, system=system)]
            fhir_contact.relationship[0].coding[0].display = display
            fhir_contact.name = cls.build_fhir_names_for_person(imis_insuree)

            if type(fhir_patient.contact) is not list:
                fhir_patient.contact = [fhir_contact]
            else:
                fhir_patient.contact.append(fhir_contact)

    @classmethod
    def build_fhir_photo(cls, fhir_patient, imis_insuree):
        if imis_insuree.photo and imis_insuree.photo.folder and imis_insuree.photo.filename:
            # HOST is taken from global variable used in the docker initialization
            abs_url = os.getenv('NEW_OPENIMIS_HOST', 'localhost')
            domain = abs_url
            photo_uri = cls.__build_photo_uri(imis_insuree)
            photo = Attachment.construct()
            parsed = urllib.parse.urlunparse(('http', domain, photo_uri, None, None, None))
            photo.url = parsed
            photo.creation = imis_insuree.photo.date.isoformat()
            photo.contentType = imis_insuree.photo.filename[imis_insuree.photo.filename.rfind('.') + 1:]
            photo.title = imis_insuree.photo.filename
            if type(fhir_patient.photo) is not list:
                fhir_patient.photo = [photo]
            else:
                fhir_patient.photo.append(photo)

    @classmethod
    def build_imis_photo(cls, imis_insuree, fhir_patient, errors):
        if fhir_patient.photo:
            if len(fhir_patient.photo) > 0:
                if fhir_patient.photo[0].data:
                    photo = fhir_patient.photo[0].data
                    date = fhir_patient.photo[0].creation
                    obj, created = \
                        InsureePhoto.objects.get_or_create(
                            chf_id=imis_insuree.chf_id,
                            defaults={
                                "photo": photo,
                                "date": date,
                                "audit_user_id": -1,
                                "officer_id": 3
                            }
                        )
                    imis_insuree.photo_id = obj.id

    @classmethod
    def build_fhir_general_practitioner(cls, fhir_patient, imis_insuree):
        if imis_insuree.health_facility:
            fhir_patient.generalPractitioner = [
                HealthcareServiceConverter.build_fhir_resource_reference(imis_insuree.health_facility, 'Practitioner')
            ]

    @classmethod
    def _family_reference_identifier_type(cls, reference_type):
        if reference_type == ReferenceConverterMixin.UUID_REFERENCE_TYPE:
            return cls.build_codeable_concept(R4IdentifierConfig.get_fhir_uuid_type_code())
        elif reference_type == ReferenceConverterMixin.DB_ID_REFERENCE_TYPE:
            return cls.build_codeable_concept(R4IdentifierConfig.get_fhir_id_type_code())
        elif reference_type == ReferenceConverterMixin.CODE_REFERENCE_TYPE:
            # Family don't have code assigned, uuid is used instead
            return cls.build_codeable_concept(R4IdentifierConfig.get_fhir_uuid_type_code())
        pass

    @classmethod
    def _family_reference_identifier_value(cls, family, reference_type):
        if reference_type == ReferenceConverterMixin.UUID_REFERENCE_TYPE:
            return family.uuid
        elif reference_type == ReferenceConverterMixin.DB_ID_REFERENCE_TYPE:
            return family.id
        elif reference_type == ReferenceConverterMixin.CODE_REFERENCE_TYPE:
            # Family don't have code assigned, uuid is used instead
            return family.uuid
        raise NotImplementedError(F"Reference type {reference_type} not implemented for family")

    @classmethod
    def __build_photo_uri(cls, imis_insuree):
        photo_folder = imis_insuree.photo.folder.replace("\\", "/")
        photo_full_path = F"{photo_folder}/{imis_insuree.photo.filename}"
        path = f'/photo/{photo_full_path}'
        return path
