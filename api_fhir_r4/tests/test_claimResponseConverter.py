import os
import json
from api_fhir_r4.converters import ClaimResponseConverter
from api_fhir_r4.models import ClaimResponseV2 as ClaimResponse
from api_fhir_r4.tests import ClaimResponseTestMixin


class ClaimResponseConverterTestCase(ClaimResponseTestMixin):

    __TEST_CLAIM_RESPONSE_JSON_PATH = "/test/test_claimResponse.json"

    def setUp(self):
        super(ClaimResponseConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_claim_response_json_representation = open(dir_path + self.__TEST_CLAIM_RESPONSE_JSON_PATH).read()

    def test_to_fhir_obj(self):
        imis_claim = self.create_test_imis_instance()
        fhir_claim_response = ClaimResponseConverter.to_fhir_obj(imis_claim)
        self.verify_fhir_instance(fhir_claim_response)

    def test_create_object_from_json(self):
        dict_claim_response = json.loads(self._test_claim_response_json_representation)
        fhir_claim_response = ClaimResponse(**dict_claim_response)
        self.verify_fhir_instance(fhir_claim_response)
