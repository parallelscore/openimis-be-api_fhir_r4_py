import json
import os

from django.utils.translation import gettext as _
from api_fhir_r4.utils import DbManagerUtils
from insuree.models import Gender
from insuree.test_helpers import create_test_insuree
from rest_framework.test import APITestCase
from rest_framework import status
from core.models import User
from core.services import create_or_update_interactive_user, create_or_update_core_user
from fhir.resources.patient import Patient
from api_fhir_r4.tests import GenericFhirAPITestMixin, PatientTestMixin, FhirApiReadTestMixin
from api_fhir_r4.configurations import GeneralConfiguration


class PatientAPITests(GenericFhirAPITestMixin, FhirApiReadTestMixin, APITestCase):

    base_url = GeneralConfiguration.get_base_url()+'Patient/'
    _test_json_path = "/test/test_patient.json"
    _TEST_LAST_NAME = "TEST_LAST_NAME"
    _TEST_LOCATION_NAME_VILLAGE = "Rachla"
    _TEST_GENDER_CODE = 'M'
    _TEST_EXPECTED_NAME = "UPDATED_NAME"
    _TEST_INSUREE_MOCKED_UUID = "7240daef-5f8f-4b0f-9042-b221e66f184a"
    _TEST_FAMILY_MOCKED_UUID = "8e33033a-9f60-43ad-be3e-3bfeb992aae5"

    _test_json_path_credentials = "/tests/test/test_login.json"
    _TEST_USER_NAME = "TestUserTest2"
    _TEST_USER_PASSWORD = "TestPasswordTest2"
    _TEST_DATA_USER = {
        "username": _TEST_USER_NAME,
        "last_name": _TEST_USER_NAME,
        "password": _TEST_USER_PASSWORD,
        "other_names": _TEST_USER_NAME,
        "user_types": "INTERACTIVE",
        "language": "en",
        "roles": [1],
    }
    _test_request_data_credentials = None

    def setUp(self):
        super(PatientAPITests, self).setUp()
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        json_representation = open(dir_path + self._test_json_path_credentials).read()
        self._test_request_data_credentials = json.loads(json_representation)
        self.get_or_create_user_api()

    def get_or_create_user_api(self):
        user = DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)
        if user is None:
            user = self.__create_user_interactive_core()
        return user

    def __create_user_interactive_core(self):
        i_user, i_user_created = create_or_update_interactive_user(
            user_id=None, data=self._TEST_DATA_USER, audit_user_id=999, connected=False)
        create_or_update_core_user(
            user_uuid=None, username=self._TEST_DATA_USER["username"], i_user=i_user)
        return DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, Patient))
        self.assertEqual(self._TEST_EXPECTED_NAME, updated_obj.name[0].given[0])

    def update_resource(self, data):
        data['name'][0]['given'][0] = self._TEST_EXPECTED_NAME

    def create_dependencies(self):
        gender = Gender()
        gender.code = self._TEST_GENDER_CODE
        gender.save()

        imis_location = PatientTestMixin().create_mocked_location()
        imis_location.save()
        # create mocked insuree with family - new insuree as a part of this test of family
        imis_mocked_insuree = create_test_insuree(with_family=True)
        imis_mocked_insuree.uuid = self._TEST_INSUREE_MOCKED_UUID
        imis_mocked_insuree.current_village = imis_location
        imis_mocked_insuree.last_name = self._TEST_LAST_NAME
        imis_mocked_insuree.save()

        # update family uuid
        imis_family = imis_mocked_insuree.family
        imis_family.uuid = self._TEST_FAMILY_MOCKED_UUID
        imis_family.location = imis_location
        imis_family.save()

    def update_payload_missing_chfid_identifier(self, data):
        for i in range(len(data["identifier"])):
            if data["identifier"][i]["type"]["coding"][0]["code"] == "Code":
                del data["identifier"][i]
                return data

    def update_payload_no_extensions(self, data):
        data["extension"] = []
        return data

    def update_payload_missing_fhir_address_details(self, data, field, kind_of_address):
        for address in data["address"]:
            if address["use"] == kind_of_address:
                address.pop(field)
        return data

    def update_payload_missing_fhir_address_extension(self, data, kind_of_extension):
        for address in data["address"]:
            if address["use"] == "home":
                for i in range(len(address["extension"])):
                    if kind_of_extension in address["extension"][i]['url']:
                        del address["extension"][i]
                        return data

    def update_payload_missing_fhir_address_extensions_all(self, data):
        for address in data["address"]:
            if address["use"] == "home":
                for i in range(len(address["extension"])):
                    address.pop("extension")
                    return data

    def update_payload_fhir_no_address(self, data):
        data["address"] = []
        return data

    def update_payload_fhir_address_no_photo(self, data):
        data.pop("photo")
        return data

    def update_payload_fhir_address_missing_photo_data(self, data):
        for photo in data["photo"]:
            photo.pop("title")
        return data

    def update_payload_fhir_address_no_name(self, data):
        data.pop("name")
        return data

    def update_payload_fhir_address_missing_name_given_field(self, data):
        for name in data["name"]:
            name.pop('given')
        return data

    def test_post_should_create_correctly(self):
        self.create_dependencies()
        response = self.client.post(
            GeneralConfiguration.get_base_url() + 'login/', data=self._test_request_data_credentials, format='json'
        )
        response_json = response.json()
        token = response_json["token"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            "Content-Type": "application/json",
            'HTTP_AUTHORIZATION': f"Bearer {token}"
        }
        response = self.client.post(self.base_url, data=self._test_request_data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.content)

    def test_post_should_raise_error_no_chfid_identifier(self):
        self.create_dependencies()
        response = self.client.post(
            GeneralConfiguration.get_base_url() + 'login/', data=self._test_request_data_credentials, format='json'
        )
        response_json = response.json()
        token = response_json["token"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            "Content-Type": "application/json",
            'HTTP_AUTHORIZATION': f"Bearer {token}"
        }
        modified_payload = self.update_payload_missing_chfid_identifier(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json', **headers)
        response_json = response.json()
        output_error_details = response_json["issue"][0]
        self.assertTrue(response.status_code, 500)
        self.assertTrue('details' in output_error_details.keys())
        self.assertEqual(output_error_details['severity'], 'error')

    def test_post_should_raise_error_no_extensions(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_no_extensions(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _("At least one extension with is_head is required")
        )

    def test_post_should_raise_missing_fhir_home_address_details(self):
        self.login()
        self.create_dependencies()
        expected_output = _('At least one of required fields for address is missing: state, district, city')
        # missing city
        modified_payload = self.update_payload_missing_fhir_address_details(data=self._test_request_data, field="city", kind_of_address="home")
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_city = response.json()
        # missing district
        modified_payload = self.update_payload_missing_fhir_address_details(data=self._test_request_data, field="district", kind_of_address="home")
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_district = response.json()
        # missing state
        modified_payload = self.update_payload_missing_fhir_address_details(data=self._test_request_data, field="state", kind_of_address="home")
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_state = response.json()
        self.assertEqual(
            response_json_city["issue"][0]["details"]["text"],
            expected_output
        )
        self.assertEqual(
            response_json_district["issue"][0]["details"]["text"],
            expected_output
        )
        self.assertEqual(
            response_json_state["issue"][0]["details"]["text"],
            expected_output
        )

    def test_post_should_raise_missing_fhir_address_home_family_extensions(self):
        self.login()
        self.create_dependencies()
        # missing municipality extension
        modified_payload = self.update_payload_missing_fhir_address_extension(data=self._test_request_data, kind_of_extension='address-municipality')
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_municipality = response.json()
        # missing all extensions
        modified_payload = self.update_payload_missing_fhir_address_extensions_all(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_no_extensions = response.json()
        self.assertEqual(
            response_json_municipality["issue"][0]["details"]["text"],
            _('At least one of required extensions for address is missing: address-location-reference or address-municipality')
        )
        self.assertEqual(
            response_json_no_extensions["issue"][0]["details"]["text"],
            _("Missing extensions for Address")
        )

    def test_post_should_raise_error_no_address(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_fhir_no_address(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('Address must be supported')
        )

    def test_post_should_raise_error_no_photo(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_fhir_address_no_photo(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('FHIR Patient without photo data.')
        )

    def test_post_should_raise_error_missing_photo_data(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_fhir_address_missing_photo_data(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('FHIR Patient misses one of required fields:  contentType, title, creation')
        )

    def test_post_should_raise_error_missing_name_attribute(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_fhir_address_missing_name_given_field(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_no_given_name = response.json()
        self.assertEqual(
            response_json_no_given_name["issue"][0]["details"]["text"],
            _('Missing obligatory fields for fhir patient name: family or given')
        )
        modified_payload = self.update_payload_fhir_address_no_name(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json_no_name = response.json()
        self.assertEqual(
            response_json_no_name["issue"][0]["details"]["text"],
            _('Missing fhir patient attribute: name')
        )
