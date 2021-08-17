from rest_framework.test import APITestCase
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiCreateTestMixin


class InsurancePlanAPITests(GenericFhirAPITestMixin, FhirApiCreateTestMixin, APITestCase):

    base_url = '/api_fhir_r4/InsurancePlan/'
    _test_json_path = "/test/test_insurance_plan.json"
    _TEST_PRODUCT_CODE = "Test0001"

    def setUp(self):
        super(InsurancePlanAPITests, self).setUp()
