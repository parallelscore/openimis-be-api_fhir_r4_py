from django.utils.translation import gettext as _
from insuree.models import Gender
from rest_framework.test import APITestCase, APIRequestFactory

from fhir.resources.patient import Patient
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiReadTestMixin, FhirApiCreateTestMixin, \
    FhirApiUpdateTestMixin, FhirApiDeleteTestMixin


class PatientAPITests(GenericFhirAPITestMixin, FhirApiReadTestMixin, FhirApiCreateTestMixin, FhirApiUpdateTestMixin,
                      FhirApiDeleteTestMixin, APITestCase):

    base_url = '/api_fhir_r4/Patient/'
    _test_json_path = "/test/test_patient.json"
    _TEST_GENDER_CODE = 'M'
    _TEST_EXPECTED_NAME = "UPDATED_NAME"

    def setUp(self):
        super(PatientAPITests, self).setUp()

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, Patient))
        self.assertEqual(self._TEST_EXPECTED_NAME, updated_obj.name[0].given[0])

    def update_resource(self, data):
        data['name'][0]['given'][0] = self._TEST_EXPECTED_NAME

    def create_dependencies(self):
        gender = Gender()
        gender.code = self._TEST_GENDER_CODE
        gender.save()

    def update_payload_missing_chfid_identifier(self, data):
        for i in range(len(data["identifier"])):
            if data["identifier"][i]["type"]["coding"][0]["code"] == "SB":
                del data["identifier"][i]
                return data

    def update_payload_no_extensions(self, data):
        data["extension"] = []
        return data

    def update_payload_missing_fhir_address_home_family(self, data):
        for i in range(len(data["address"])):
            if data["address"][i]['use'] == "home":
                del data["address"][i]
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

    def update_payload_fhir_address_temp(self, data):
        for address in data["address"]:
            if address["use"] == "home":
                address["use"] = "temp"
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

    #def update_payload_remove_chf_id_from_it(self, data):
    #    for member in data["member"]:
    #        member["entity"]["identifier"].pop("value")
    #    return data

    def test_post_should_raise_error_no_chfid_identifier(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_missing_chfid_identifier(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        splited_output = response_json["issue"][0]["details"]["text"].split(" ")
        self.assertEqual(
            splited_output[2] + " " + splited_output[3],
            _("without code")
        )

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

    def test_post_should_raise_missing_fhir_address_home_family(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_missing_fhir_address_home_family(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('Address must be supported')
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

    def test_post_should_raise_error_no_family_address_slice(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_fhir_address_temp(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('Patient without family address')
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
