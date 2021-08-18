import json
import os

from api_fhir_r4.converters import InsurancePlanConverter
from collections import OrderedDict
from django.core.serializers.json import DjangoJSONEncoder

from fhir.resources.insuranceplan import InsurancePlan
from api_fhir_r4.tests import InsurancePlanTestMixin


class InsurancePlanConverterTestCase(InsurancePlanTestMixin):

    __TEST_INSURANCE_PLAN_JSON_PATH = "/test/test_insurance_plan.json"

    def setUp(self):
        super(InsurancePlanConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_insurance_plan_json_representation = open(dir_path + self.__TEST_INSURANCE_PLAN_JSON_PATH).read()

    def test_to_fhir_obj(self):
        self.setUp()
        imis_product = self.create_test_imis_instance()
        fhir_insurance_plan = InsurancePlanConverter.to_fhir_obj(imis_product)
        self.verify_fhir_instance(fhir_insurance_plan)

    def test_to_imis_obj(self):
        self.setUp()
        fhir_insurance_plan = self.create_test_fhir_instance()
        imis_product = InsurancePlanConverter.to_imis_obj(fhir_insurance_plan.dict(), None)
        self.verify_imis_instance(imis_product)

    def test_create_object_from_json(self):
        self.setUp()
        dict_insurance_plan = json.loads(self._test_insurance_plan_json_representation)
        fhir_insurance_plan = InsurancePlan(**dict_insurance_plan)
        self.verify_fhir_instance(fhir_insurance_plan)
