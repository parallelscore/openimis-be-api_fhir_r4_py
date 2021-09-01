import json
import os

from api_fhir_r4.converters import ContractConverter
from api_fhir_r4.tests import ContractTestMixin
from fhir.resources.contract import Contract


class ContractConverterTestCase(ContractTestMixin):

    __TEST_CONTRACT_JSON_PATH = "/test/test_contract.json"

    def setUp(self):
        super(ContractConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_contract_json_representation = open(dir_path + self.__TEST_CONTRACT_JSON_PATH).read()

    def test_to_fhir_obj(self):
        self.setUp()
        imis_policy = self.create_test_imis_instance()
        fhir_contract = ContractConverter.to_fhir_obj(imis_policy)
        self.verify_fhir_instance(fhir_contract)

    def test_to_imis_obj(self):
        self.setUp()
        fhir_contract = self.create_test_fhir_instance()
        imis_policy = ContractConverter.to_imis_obj(fhir_contract.dict(), None)
        self.verify_imis_instance(imis_policy)

    def test_create_object_from_json(self):
        self.setUp()
        dict_contract = json.loads(self._test_contract_json_representation)
        fhir_contract = Contract(**dict_contract)
        self.verify_fhir_instance(fhir_contract)
