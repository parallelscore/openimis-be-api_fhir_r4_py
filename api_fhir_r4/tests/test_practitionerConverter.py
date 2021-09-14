import json
import os

from api_fhir_r4.converters import PractitionerConverter

from fhir.resources.practitioner import Practitioner
from api_fhir_r4.tests import PractitionerTestMixin


class PractitionerConverterTestCase(PractitionerTestMixin):

    __TEST_PRACTITIONER_JSON_PATH = "/test/test_practitioner.json"

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_practitioner_json_representation = open(dir_path + self.__TEST_PRACTITIONER_JSON_PATH).read()

    def test_to_fhir_obj(self):
        imis_claim_admin = self.create_test_imis_instance()
        fhir_practitioner = PractitionerConverter.to_fhir_obj(imis_claim_admin)
        self.verify_fhir_instance(fhir_practitioner)

    def test_to_imis_obj(self):
        fhir_practitioner = self.create_test_fhir_instance()
        imis_claim_admin = PractitionerConverter.to_imis_obj(fhir_practitioner.dict(), None)
        self.verify_imis_instance(imis_claim_admin)

    def test_create_object_from_json(self):
        self.setUp()
        dict_practitioner = json.loads(self._test_practitioner_json_representation)
        fhir_practitioner = Practitioner(**dict_practitioner)
        self.verify_fhir_instance(fhir_practitioner)
