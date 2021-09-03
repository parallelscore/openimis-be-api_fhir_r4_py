import json
import os

from api_fhir_r4.converters.locationConverter import LocationConverter
from fhir.resources.location import Location
from api_fhir_r4.tests import LocationTestMixin


class LocationConverterTestCase(LocationTestMixin):

    __TEST_LOCATION_JSON_PATH = "/test/test_location.json"

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_location_json_representation = open(dir_path + self.__TEST_LOCATION_JSON_PATH).read()

    def test_to_fhir_obj(self):
        imis_hf = self.create_test_imis_instance()
        fhir_location = LocationConverter.to_fhir_obj(imis_hf)
        self.verify_fhir_instance(fhir_location)

    def test_to_imis_obj(self):
        fhir_loaction = self.create_test_fhir_instance()
        imis_hf = LocationConverter.to_imis_obj(fhir_loaction.dict(), None)
        self.verify_imis_instance(imis_hf)

    def test_create_object_from_json(self):
        self.setUp()
        dict_location = json.loads(self._test_location_json_representation)
        fhir_location = Location(**dict_location)
        self.verify_fhir_instance(fhir_location)
