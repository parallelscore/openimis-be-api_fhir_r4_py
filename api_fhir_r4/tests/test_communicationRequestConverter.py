import json
import os

from api_fhir_r4.converters import CommunicationRequestConverter
from fhir.resources.communicationrequest import CommunicationRequest
from api_fhir_r4.tests import CommunicationRequestTestMixin


class CommunicationRequestConverterTestCase(CommunicationRequestTestMixin):

    __TEST_COMMUNICATION_REQUEST_JSON_PATH = "/test/test_communicationRequest.json"

    def setUp(self):
        super(CommunicationRequestConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_communication_request_json_representation = open(dir_path + self.__TEST_COMMUNICATION_REQUEST_JSON_PATH).read()
        # .dumps() will not put a newline at the end of the "file" but editors will
        if self._test_communication_request_json_representation[-1:] == "\n":
            self._test_communication_request_json_representation = self._test_communication_request_json_representation[:-1]

    def test_to_fhir_obj(self):
        imis_feedback = self.create_test_imis_instance()
        fhir_communication_request = CommunicationRequestConverter.to_fhir_obj(imis_feedback)
        self.verify_fhir_instance(fhir_communication_request)

    def test_fhir_object_to_json_request(self):
        self.setUp()
        dict_communication_request = json.loads(self._test_communication_request_json_representation)
        fhir_communication_request = CommunicationRequest(**dict_communication_request)
        self.verify_fhir_instance(fhir_communication_request)
