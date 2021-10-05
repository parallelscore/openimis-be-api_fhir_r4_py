import json
import os

from api_fhir_r4.tests import GenericFhirAPITestMixin
from api_fhir_r4.configurations import GeneralConfiguration
from core.models import User
from core.services import create_or_update_interactive_user, create_or_update_core_user
from rest_framework import status
from rest_framework.test import APITestCase
from api_fhir_r4.utils import DbManagerUtils


class CommunicationRequestAPITests(GenericFhirAPITestMixin, APITestCase):

    base_url = GeneralConfiguration.get_base_url()+'CommunicationRequest/'
    _test_json_path = "/test/test_communicationRequest.json"

    _test_json_path_credentials = "/tests/test/test_login.json"
    _TEST_USER_NAME = "TestUserTest2"
    _TEST_USER_PASSWORD = "TestPasswordTest2"
    _TEST_DATA_USER = {
        "username": _TEST_USER_NAME,
        "last_name": _TEST_USER_NAME,
        "password": _TEST_USER_PASSWORD,
        "other_names": _TEST_USER_NAME,
        "user_types": "INTERACTIVE",
        "language": "en",
        "roles": [5],
    }
    _test_request_data_credentials = None

    def setUp(self):
        super(CommunicationRequestAPITests, self).setUp()
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        json_representation = open(dir_path + self._test_json_path_credentials).read()
        self._test_request_data_credentials = json.loads(json_representation)
        self._TEST_USER = self.get_or_create_user_api()


    def get_or_create_user_api(self):
        user = DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)
        if user is None:
            user = self.__create_user_interactive_core()
        return user

    def __create_user_interactive_core(self):
        i_user, i_user_created = create_or_update_interactive_user(
            user_id=None, data=self._TEST_DATA_USER, audit_user_id=999, connected=False
        )
        create_or_update_core_user(
            user_uuid=None, username=self._TEST_DATA_USER["username"], i_user=i_user
        )
        return DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)

    def test_get_should_return_200(self):
        # test if return 200
        response = self.client.post(
            GeneralConfiguration.get_base_url() + 'login/', data=self._test_request_data_credentials, format='json'
        )
        response_json = response.json()
        token = response_json["token"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            "Content-Type": "application/json",
            "HTTP_AUTHORIZATION": f"Bearer {token}"
        }
        response = self.client.get(self.base_url, data=None, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
