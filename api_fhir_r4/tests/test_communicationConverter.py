import json
import os

from api_fhir_r4.converters import CommunicationConverter
from api_fhir_r4.tests import CommunicationTestMixin
from fhir.resources.communication import Communication


class CommunicationConverterTestCase(CommunicationTestMixin):

    __TEST_COMMUNICATION_JSON_PATH = "/test/test_communication.json"

    def setUp(self):
        super(CommunicationConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_communication_json_representation = open(dir_path + self.__TEST_COMMUNICATION_JSON_PATH).read()

    def test_to_fhir_obj(self):
        imis_feedback = self.create_test_imis_instance()
        fhir_communication = CommunicationConverter.to_fhir_obj(imis_feedback)
        self.verify_fhir_instance(fhir_communication)

    def test_to_imis_obj(self):
        fhir_communication = self.create_test_fhir_instance()
        imis_feedback = CommunicationConverter.to_imis_obj(fhir_communication.dict(), None)
        self.verify_imis_instance(imis_feedback)

    def test_create_object_from_json(self):
        dict_communication = json.loads(self._test_communication_json_representation)
        fhir_communication = Communication(**dict_communication)
        self.verify_fhir_instance(fhir_communication)
