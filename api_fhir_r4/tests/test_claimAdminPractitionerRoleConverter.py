import json
import os

from api_fhir_r4.converters import ClaimAdminPractitionerRoleConverter
from fhir.resources.practitionerrole import PractitionerRole
from api_fhir_r4.tests import ClaimAdminPractitionerRoleTestMixin


class ClaimAdminPractitionerRoleConverterTestCase(ClaimAdminPractitionerRoleTestMixin):

    __TEST_PRACTITIONER_ROLE_JSON_PATH = "/test/test_claimAdminPractitionerRole.json"

    def setUp(self):
        super(ClaimAdminPractitionerRoleConverterTestCase, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._test_practitioner_role_json_representation = open(
            dir_path + self.__TEST_PRACTITIONER_ROLE_JSON_PATH).read()
        if self._test_practitioner_role_json_representation[-1:] == "\n":
            self._test_practitioner_role_json_representation = self._test_practitioner_role_json_representation[:-1]

    def test_to_fhir_obj(self):
        imis_claim_admin = self.create_test_imis_instance()
        fhir_practitioner_role = ClaimAdminPractitionerRoleConverter.to_fhir_obj(imis_claim_admin)
        self.verify_fhir_instance(fhir_practitioner_role)

    def test_to_imis_obj(self):
        fhir_practitioner_role = self.create_test_fhir_instance()
        imis_claim_admin = ClaimAdminPractitionerRoleConverter.to_imis_obj(fhir_practitioner_role.dict(), None)
        self.verify_imis_instance(imis_claim_admin)

    def test_create_object_from_json(self):
        dict_practitioner_role = json.loads(self._test_practitioner_role_json_representation)
        fhir_practitioner_role = PractitionerRole(**dict_practitioner_role)
        self.verify_fhir_instance(fhir_practitioner_role)
