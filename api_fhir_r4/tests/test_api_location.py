from rest_framework.test import APITestCase

from fhir.resources.location import Location
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiCreateTestMixin, \
    FhirApiUpdateTestMixin


class LocationAPITests(GenericFhirAPITestMixin, FhirApiCreateTestMixin, FhirApiUpdateTestMixin,
                       APITestCase):

    base_url = '/api_fhir_r4/Location/'
    _test_json_path = "/test/test_location.json"
    _TEST_EXPECTED_NAME = "UPDATED_NAME"

    def setUp(self):
        super(LocationAPITests, self).setUp()

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, Location))
        self.assertEqual(self._TEST_EXPECTED_NAME, updated_obj.name)

    def update_resource(self, data):
        data['name'] = self._TEST_EXPECTED_NAME
