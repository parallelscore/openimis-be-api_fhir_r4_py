from django.utils.translation import gettext as _
from rest_framework.test import APITestCase
from fhir.resources.insuranceplan import InsurancePlan
from api_fhir_r4.tests import GenericFhirAPITestMixin, FhirApiCreateTestMixin, \
    FhirApiUpdateTestMixin, FhirApiReadTestMixin
from api_fhir_r4.configurations import  GeneralConfiguration


class InsurancePlanAPITests(GenericFhirAPITestMixin, FhirApiReadTestMixin, FhirApiCreateTestMixin,
                            FhirApiUpdateTestMixin, APITestCase):

    base_url = GeneralConfiguration.get_base_url()+'InsurancePlan/'
    _test_json_path = "/test/test_insurance_plan.json"
    _TEST_PRODUCT_CODE = "Test0001"
    _TEST_MAX_INSTALLMENTS = 4

    def setUp(self):
        super(InsurancePlanAPITests, self).setUp()

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, InsurancePlan))
        max_installments_data = None
        for extension in updated_obj.extension:
            if "max-installments" in extension.url:
                max_installments_data = extension
        self.assertEqual(self._TEST_MAX_INSTALLMENTS, max_installments_data.valueUnsignedInt)

    def update_resource(self, data):
        for extension in data["extension"]:
            if "max-installments" in extension["url"]:
                extension["valueUnsignedInt"] = self._TEST_MAX_INSTALLMENTS

    def update_payload_missing_code_identifier(self, data):
        for i in range(len(data["identifier"])):
            if data["identifier"][i]["type"]["coding"][0]["code"] == "IC":
                del data["identifier"][i]
                return data

    def test_post_should_raise_error_no_code_identifier(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_missing_code_identifier(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        splited_output = response_json["issue"][0]["details"]["text"].split(" ")
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _("InsurancePlan FHIR without code - this field is obligatory")
        )
