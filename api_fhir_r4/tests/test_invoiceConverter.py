import os

from api_fhir_r4.converters import InvoiceConverter
from api_fhir_r4.tests.mixin.invoiceTestMixin import InvoiceTestMixin
from api_fhir_r4.tests.mixin.logInMixin import LogInMixin


class InvoiceConverterTestCase(InvoiceTestMixin, LogInMixin):
    _TEST_USER_NAME = "TestUserTest2"
    __TEST_INVOICE_JSON_PATH = "/test/test_invoice.json"

    @classmethod
    def setUpClass(cls):
        super(InvoiceConverterTestCase, cls).setUpClass()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        cls.__TEST_INVOICE_JSON_TEXT__ = open(dir_path + cls.__TEST_INVOICE_JSON_PATH).read()

    def setUp(self):
        super(InvoiceConverterTestCase, self).setUp()

    def test_to_fhir_obj(self):
        user = self.get_or_create_user_api()
        imis_invoice, imis_invoice_line_item = self.create_test_imis_instance()
        imis_invoice.save(username=user.username)
        imis_invoice_line_item.save(username=user.username)
        fhir_invoice = InvoiceConverter.to_fhir_obj(imis_invoice)
        self.verify_fhir_instance(fhir_invoice)
        imis_invoice_line_item.delete(username=user.username)
        imis_invoice.delete(username=user.username)

    def test_to_imis_obj(self):
        self.assertRaises(NotImplementedError, InvoiceConverter.to_imis_obj, object(), 1)
