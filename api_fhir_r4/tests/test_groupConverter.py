import json
import os

from api_fhir_r4.converters import GroupConverter

from fhir.resources.group import Group
from api_fhir_r4.tests import GroupTestMixin


class GroupConverterTestCase(GroupTestMixin):

    __TEST_GROUP_JSON_PATH = "/test/test_group.json"

    def setUp(self):
        super(GroupConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_group_json_representation = open(dir_path + self.__TEST_GROUP_JSON_PATH).read()

    def test_to_fhir_obj(self):
        self.setUp()
        imis_family = self.create_test_imis_instance()
        fhir_group = GroupConverter.to_fhir_obj(imis_family)
        self.verify_fhir_instance(fhir_group)

    def test_to_imis_obj(self):
        self.setUp()
        fhir_group = self.create_test_fhir_instance()
        imis_family = GroupConverter.to_imis_obj(fhir_group.dict(), None)
        self.verify_imis_instance(imis_family)

    def test_create_object_from_json(self):
        self.setUp()
        dict_group = json.loads(self._test_group_json_representation)
        fhir_group = Group(**dict_group)
        self.verify_fhir_instance(fhir_group)

