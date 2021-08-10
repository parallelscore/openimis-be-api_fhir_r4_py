from insuree.test_helpers import *
from rest_framework.test import APITestCase
from fhir.resources.group import Group
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiReadTestMixin, FhirApiCreateTestMixin, \
    FhirApiUpdateTestMixin, FhirApiDeleteTestMixin


class GroupAPITests(GenericFhirAPITestMixin, FhirApiReadTestMixin, FhirApiCreateTestMixin, FhirApiUpdateTestMixin,
                      FhirApiDeleteTestMixin, APITestCase):

    base_url = '/api_fhir_r4/Group/'
    _test_json_path = "/test/test_group.json"
    _TEST_INSUREE_CHFID = "TestCfhId1"
    _TEST_INSUREE_LAST_NAME = "Test"
    _TEST_INSUREE_OTHER_NAMES = "TestInsuree"
    _TEST_POVERTY_STATUS = True

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
