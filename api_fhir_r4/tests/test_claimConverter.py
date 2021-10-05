import json
import os


from api_fhir_r4.converters.claimConverter import ClaimConverter
from api_fhir_r4.models import ClaimV2 as Claim
from api_fhir_r4.tests import ClaimTestMixin


class ClaimConverterTestCase(ClaimTestMixin):

    __TEST_CLAIM_JSON_PATH = "/test/test_claim.json"

    def setUp(self):
        super(ClaimConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_claim_json_representation = open(dir_path + self.__TEST_CLAIM_JSON_PATH).read()
        if self._test_claim_json_representation[-1:] == "\n":
            self._test_claim_json_representation = self._test_claim_json_representation[:-1]

    def test_to_fhir_obj(self):
        imis_claim = self.create_test_imis_instance()
        fhir_claim = ClaimConverter.to_fhir_obj(imis_claim)
        self.verify_fhir_instance(fhir_claim)

    def test_to_imis_obj(self):
        fhir_claim = self.create_test_fhir_instance()
        imis_claim = ClaimConverter.to_imis_obj(fhir_claim.dict(), None)
        self.verify_imis_instance(imis_claim)

    def test_create_object_from_json(self):
        dict_claim = json.loads(self._test_claim_json_representation)
        fhir_claim = Claim(**dict_claim)
        self.verify_fhir_instance(fhir_claim)
