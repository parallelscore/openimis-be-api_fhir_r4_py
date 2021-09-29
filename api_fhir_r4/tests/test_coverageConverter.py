import json
import os

from api_fhir_r4.converters.coverageConverter import CoverageConverter
from api_fhir_r4.tests import CoverageTestMixin
from api_fhir_r4.models import CoverageV2 as Coverage


class CoverageConverterTestCase(CoverageTestMixin):

    __TEST_COVERAGE_JSON_PATH = "/test/test_coverage.json"

    def setUp(self):
        super(CoverageConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_coverage_json_representation = open(dir_path + self.__TEST_COVERAGE_JSON_PATH).read()

    def test_to_fhir_obj(self):
        self.setUp()
        imis_policy = self.create_test_imis_instance()
        fhir_coverage = CoverageConverter.to_fhir_obj(imis_policy)
        self.verify_fhir_instance(fhir_coverage)

    def test_create_object_from_json(self):
        self.setUp()
        dict_coverage = json.loads(self._test_coverage_json_representation)
        fhir_coverage = Coverage(**dict_coverage)
        self.verify_fhir_instance(fhir_coverage)
