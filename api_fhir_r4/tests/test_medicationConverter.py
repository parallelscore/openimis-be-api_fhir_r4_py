import json
import os

from api_fhir_r4.converters import MedicationConverter

from fhir.resources.medication import Medication
from api_fhir_r4.tests import MedicationTestMixin


class MedicationConverterTestCase(MedicationTestMixin):

    __TEST_MEDICATION_JSON_PATH = "/test/test_medication.json"

    def setUp(self):
        super(MedicationConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_medication_json_representation = open(dir_path + self.__TEST_MEDICATION_JSON_PATH).read()

    def test_to_fhir_obj(self):
        self.setUp()
        imis_item = self.create_test_imis_instance()
        fhir_medication = MedicationConverter.to_fhir_obj(imis_item)
        self.verify_fhir_instance(fhir_medication)

    def test_to_imis_obj(self):
        self.setUp()
        fhir_medication = self.create_test_fhir_instance()
        imis_item = MedicationConverter.to_imis_obj(fhir_medication.dict(), None)
        self.verify_imis_instance(imis_item)

    def test_create_object_from_json(self):
        self.setUp()
        dict_medication = json.loads(self._test_medication_json_representation)
        fhir_medication = Medication(**dict_medication)
        self.verify_fhir_instance(fhir_medication)
