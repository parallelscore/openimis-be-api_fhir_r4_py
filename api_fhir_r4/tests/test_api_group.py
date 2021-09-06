from django.utils.translation import gettext as _
from insuree.test_helpers import *
from rest_framework import status
from rest_framework.test import APITestCase
from fhir.resources.group import Group
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiReadTestMixin, FhirApiCreateTestMixin, \
    FhirApiUpdateTestMixin, FhirApiDeleteTestMixin, GroupTestMixin


class GroupAPITests(GenericFhirAPITestMixin, FhirApiCreateTestMixin, FhirApiUpdateTestMixin,
                       APITestCase):

    base_url = '/api_fhir_r4/Group/'
    _test_json_path = "/test/test_group.json"
    _TEST_INSUREE_CHFID = "TestCfhId1"
    _TEST_INSUREE_LAST_NAME = "Test"
    _TEST_INSUREE_OTHER_NAMES = "TestInsuree"
    _TEST_POVERTY_STATUS = True
    _TEST_INSUREE_CHFID_NOT_EXIST = "NotExistedCHF"

    def setUp(self):
        super(GroupAPITests, self).setUp()

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, Group))
        poverty_data = None
        for extension in updated_obj.extension:
            if "group-poverty-status" in extension.url:
                poverty_data = extension
        self.assertEqual(self._TEST_POVERTY_STATUS, poverty_data.valueBoolean)

    def update_resource(self, data):
        for extension in data["extension"]:
            if "group-poverty-status" in extension["url"]:
                extension["valueBoolean"] = self._TEST_POVERTY_STATUS

    def create_dependencies(self):
        insuree = create_test_insuree(
            with_family=False,
            custom_props=
            {
                "chf_id": self._TEST_INSUREE_CHFID,
                "last_name": self._TEST_INSUREE_LAST_NAME,
                "other_names": self._TEST_INSUREE_OTHER_NAMES,
            }
        )
        imis_location = GroupTestMixin().create_mocked_location()
        imis_location.save()

    def update_payload_no_extensions(self, data):
        data["extension"] = []
        return data

    def update_payload_no_such_chf_id(self, data):
        for member in data["member"]:
            member["entity"]["identifier"]["value"] = self._TEST_INSUREE_CHFID_NOT_EXIST
        return data

    def update_payload_remove_chf_id_from_it(self, data):
        for member in data["member"]:
            member["entity"]["identifier"].pop("value")
        return data

    def test_post_should_raise_error_no_extensions(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_no_extensions(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _("At least one extension with address is required")
        )

    def test_post_should_raise_error_no_such_chf_id(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_no_such_chf_id(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('Such insuree %(chf_id)s does not exist') % {'chf_id': self._TEST_INSUREE_CHFID_NOT_EXIST}
        )

    def test_post_should_raise_error_no_chf_id_in_payload(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_remove_chf_id_from_it(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _("Family Group FHIR without code - this field is obligatory")
        )
