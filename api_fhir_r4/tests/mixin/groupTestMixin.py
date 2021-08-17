"""
from uuid import UUID

from insuree.models import Family, Insuree

from api_fhir_r4.configurations import R4IdentifierConfig, R4MaritalConfig
from api_fhir_r4.converters import PatientConverter
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.group import Group
from api_fhir_r4.tests import GenericTestMixin
from api_fhir_r4.utils import TimeUtils


class GroupTestMixin(GenericTestMixin):

    _TEST_NAME = "TEST_LAST_NAME"
    _TEST_HEAD_INSUREE = None
    _TEST_LOCATION = "Location/Rachla-village"
    _TEST_POVERTY = False
    _TEST_FAMILY_TYPE = ""
    _TEST_ADDRESS = ""
    _TEST_ETHNICITY = ""
    _TEST_CONFIRMATION_NUMBER = "NO1234"
    _TEST_CONFIRMATION_TYPE = ""

    def setUp(self):
        #self._TEST_GENDER = Gender()
        #self._TEST_GENDER.code = self._TEST_GENDER_CODE
        pass

    def create_test_imis_instance(self):
        self.setUp()
        imis_family = Family()
        imis_family.head_insuree = self._TEST_LAST_NAME
        imis_family.location = self._TEST_LOCATION
        imis_family.poverty = self._TEST_ID
        imis_family.family_type = self._TEST_UUID
        imis_family.confirmation_no = self._TEST_CHF_ID
        imis_family.confirmation_type = TimeUtils.str_to_date(self._TEST_DOB)
        return imis_family

    def verify_imis_instance(self, imis_obj):
        self.assertEqual(self._TEST_LAST_NAME, imis_obj.last_name)
        self.assertEqual(self._TEST_OTHER_NAME, imis_obj.other_names)
        self.assertEqual(self._TEST_CHF_ID, imis_obj.chf_id)
        self.assertEqual(self._TEST_PASSPORT, imis_obj.passport)
        expected_date = TimeUtils.str_to_date(self._TEST_DOB)
        self.assertEqual(expected_date, imis_obj.dob)
        self.assertEqual(self._TEST_GENDER_CODE, imis_obj.gender.code)
        self.assertEqual("D", imis_obj.marital)
        self.assertEqual(self._TEST_PHONE, imis_obj.phone)
        self.assertEqual(self._TEST_EMAIL, imis_obj.email)
        self.assertEqual(self._TEST_ADDRESS, imis_obj.current_address)
        self.assertEqual(self._TEST_GEOLOCATION, imis_obj.geolocation)

    def create_test_fhir_instance(self):
        fhir_family = Group.construct()
        name = HumanName.construct()
        name.family = self._TEST_LAST_NAME
        name.given = [self._TEST_OTHER_NAME]
        name.use = "usual"
        fhir_patient.name = [name]
        identifiers = []
        chf_id = PatientConverter.build_fhir_identifier(self._TEST_CHF_ID,
                                                        R4IdentifierConfig.get_fhir_identifier_type_system(),
                                                        R4IdentifierConfig.get_fhir_chfid_type_code())

        identifiers.append(chf_id)
        passport = PatientConverter.build_fhir_identifier(self._TEST_PASSPORT,
                                                          R4IdentifierConfig.get_fhir_identifier_type_system(),
                                                          R4IdentifierConfig.get_fhir_passport_type_code())
        identifiers.append(passport)
        fhir_patient.identifier = identifiers
        fhir_patient.birthDate = self._TEST_DOB
        fhir_patient.gender = "male"
        fhir_patient.maritalStatus = PatientConverter.build_codeable_concept(
            R4MaritalConfig.get_fhir_divorced_code(),
            R4MaritalConfig.get_fhir_marital_status_system())
        telecom = []
        phone = PatientConverter.build_fhir_contact_point(self._TEST_PHONE, "phone",
                                                          "home")
        telecom.append(phone)
        email = PatientConverter.build_fhir_contact_point(self._TEST_EMAIL, "email",
                                                          "home")
        telecom.append(email)
        fhir_patient.telecom = telecom
        addresses = []
        current_address = PatientConverter.build_fhir_address(self._TEST_ADDRESS, "home",
                                                              "physical")
        addresses.append(current_address)
        geolocation = PatientConverter.build_fhir_address(self._TEST_GEOLOCATION, "home",
                                                          "both")
        addresses.append(geolocation)
        fhir_patient.address = addresses
        return fhir_patient

    def verify_fhir_instance(self, fhir_obj):
        self.assertEqual(1, len(fhir_obj.name))
        human_name = fhir_obj.name[0]
        self.assertTrue(isinstance(human_name, HumanName))
        self.assertEqual(self._TEST_OTHER_NAME, human_name.given[0])
        self.assertEqual(self._TEST_LAST_NAME, human_name.family)
        self.assertEqual("usual", human_name.use)
        for identifier in fhir_obj.identifier:
            self.assertTrue(isinstance(identifier, Identifier))
            code = PatientConverter.get_first_coding_from_codeable_concept(identifier.type).code
            if code == R4IdentifierConfig.get_fhir_chfid_type_code():
                self.assertEqual(self._TEST_CHF_ID, identifier.value)
            elif code == R4IdentifierConfig.get_fhir_uuid_type_code() and not isinstance(identifier.value, UUID):
                self.assertEqual(self._TEST_UUID, identifier.value)
            elif code == R4IdentifierConfig.get_fhir_passport_type_code():
                self.assertEqual(self._TEST_PASSPORT, identifier.value)
        self.assertEqual(self._TEST_DOB, fhir_obj.birthDate)
        self.assertEqual("male", fhir_obj.gender)
        marital_code = PatientConverter.get_first_coding_from_codeable_concept(fhir_obj.maritalStatus).code
        self.assertEqual(R4MaritalConfig.get_fhir_divorced_code(), marital_code)
        self.assertEqual(2, len(fhir_obj.telecom))
        for telecom in fhir_obj.telecom:
            self.assertTrue(isinstance(telecom, ContactPoint))
            if telecom.system == "phone":
                self.assertEqual(self._TEST_PHONE, telecom.value)
            elif telecom.system == "email":
                self.assertEqual(self._TEST_EMAIL, telecom.value)
        self.assertEqual(2, len(fhir_obj.address))
        for adddress in fhir_obj.address:
            self.assertTrue(isinstance(adddress, Address))
            if adddress.type == "physical":
                self.assertEqual(self._TEST_ADDRESS, adddress.text)
            elif adddress.type == "both":
                self.assertEqual(self._TEST_GEOLOCATION, adddress.text)
    """
