from unittest import mock

from django.contrib.contenttypes.models import ContentType
from policy.models import Policy

from api_fhir_r4.configurations import R4IdentifierConfig
from api_fhir_r4.tests import GenericTestMixin
from api_fhir_r4.tests.mixin import FhirConverterTestMixin
from insuree.models import Family
from invoice.models import Invoice, InvoiceLineItem
from fhir.resources.invoice import Invoice as FHIRInvoice
from api_fhir_r4.utils.timeUtils import TimeUtils


class InvoiceTestMixin(GenericTestMixin, FhirConverterTestMixin):
    _TEST_INVOICE_STATUS = 'active'
    _TEST_INVOICE_UUID = '12345678-1234-1234-1234-123456789012'
    _TEST_INVOICE_CODE = 'TEST-CODE'
    _TEST_INVOICE_SUBJECT_TYPE = ContentType.objects.get(model='Family')
    _TEST_INVOICE_SUBJECT_TYPE_CODING = 'contribution'
    _TEST_INVOICE_THIRD_PARTY = Family()
    _TEST_INVOICE_THIRD_PARTY_UUID = '98765432-1234-1234-1234-123456789012'
    _TEST_INVOICE_DATE = TimeUtils.str_iso_to_date('2021-01-01')
    _TEST_INVOICE_TOTAL_NET = 10000.0
    _TEST_INVOICE_TOTAL_GROSS = 10000.0
    _TEST_INVOICE_CURRENCY = 'USD'
    _TEST_LINE_ITEM_CHARGE_ITEM = ContentType.objects.get(model='Policy')
    _TEST_LINE_ITEM_CHARGE_ITEM_CODING = 'policy'
    _TEST_LiNE_ITEM_QUANTITY = 2
    _TEST_LINE_ITEM_UNIT_PRICE = 5000.0
    _TEST_LINE_ITEM_BASE_PRICE_COMPONENT_TYPE = 'base'
    _TEST_LINE_ITEM_DISCOUNT_COMPONENT_TYPE = 'discount'
    _TEST_LINE_ITEM_DISCOUNT = 0.1
    _TEST_LINE_ITEM_DEDUCTION_PRICE_COMPONENT_TYPE = 'deduction'
    _TEST_LINE_ITEM_DEDUCTION = 100
    _TEST_LINE_ITEM_DEDUCTION_FACTOR = 1
    _TEST_LINE_ITEM_TAX_PRICE_COMPONENT_TYPE = 'tax'
    _TEST_LINE_ITEM_TAX_RATE = 0.02

    def create_test_imis_instance(self):
        imis_invoice = Invoice()
        imis_invoice.uuid = self._TEST_INVOICE_UUID
        imis_invoice.code = self._TEST_INVOICE_CODE
        imis_invoice.subject_type = self._TEST_INVOICE_SUBJECT_TYPE
        imis_invoice.thirdparty = self._TEST_INVOICE_THIRD_PARTY
        imis_invoice.thirdparty.uuid = self._TEST_INVOICE_THIRD_PARTY_UUID
        imis_invoice.date_invoice = self._TEST_INVOICE_DATE
        imis_invoice.amount_net = self._TEST_INVOICE_TOTAL_NET
        imis_invoice.amount_total = self._TEST_INVOICE_TOTAL_GROSS
        imis_invoice.currency_code = self._TEST_INVOICE_CURRENCY

        imis_invoice_line_item = InvoiceLineItem()
        imis_invoice_line_item.line_type = self._TEST_LINE_ITEM_CHARGE_ITEM
        imis_invoice_line_item.quantity = self._TEST_LiNE_ITEM_QUANTITY
        imis_invoice_line_item.unit_price = self._TEST_LINE_ITEM_UNIT_PRICE
        imis_invoice_line_item.discount = self._TEST_LINE_ITEM_DISCOUNT
        imis_invoice_line_item.deduction = self._TEST_LINE_ITEM_DEDUCTION
        imis_invoice_line_item.tax_rate = self._TEST_LINE_ITEM_TAX_RATE

        with mock.patch('django.db.models.fields.related_descriptors.create_reverse_many_to_one_manager') as mock_patch:
            class MockedManager(mock.MagicMock):
                def all(self):
                    return [imis_invoice_line_item]

            mock_patch.return_value = MockedManager()
            # noinspection PyStatementEffect,PyUnresolvedReferences
            imis_invoice.line_items  # This call assigns mocked related manager to the model

        return imis_invoice

    def verify_imis_instance(self, imis_obj):
        raise NotImplementedError('verify_imis_instance() not implemented')

    def create_test_fhir_instance(self):
        raise NotImplementedError('create_test_fhir_instance() not implemented')

    def verify_fhir_instance(self, fhir_obj):
        self.assertIs(type(fhir_obj), FHIRInvoice)
        self.assertEqual(fhir_obj.status, self._TEST_INVOICE_STATUS)
        self.verify_fhir_identifier(fhir_obj, R4IdentifierConfig.get_fhir_uuid_type_code(), self._TEST_INVOICE_UUID)
        self.verify_fhir_identifier(fhir_obj, R4IdentifierConfig.get_fhir_generic_type_code(), self._TEST_INVOICE_CODE)
        self.verify_fhir_coding_exists(fhir_obj.type.coding, self._TEST_INVOICE_SUBJECT_TYPE_CODING)
        self.assertTrue(self._TEST_INVOICE_THIRD_PARTY_UUID in fhir_obj.recipient.reference)
        self.assertEqual(fhir_obj.date, self._TEST_INVOICE_DATE)
        self.assertEqual(fhir_obj.totalNet.value, self._TEST_INVOICE_TOTAL_NET, 1e-10)
        self.assertEqual(fhir_obj.totalNet.currency, self._TEST_INVOICE_CURRENCY)
        self.assertEqual(fhir_obj.totalGross.value, self._TEST_INVOICE_TOTAL_GROSS, 1e-10)
        self.assertEqual(fhir_obj.totalGross.currency, self._TEST_INVOICE_CURRENCY)

        self.assertGreater(len(fhir_obj.lineItem), 0)
        self.verify_fhir_coding_exists(fhir_obj.lineItem[0].chargeItemCodeableConcept.coding,
                                       self._TEST_LINE_ITEM_CHARGE_ITEM_CODING)
        self.assertGreater(len(fhir_obj.lineItem[0].priceComponent), 0)
        for price_component in fhir_obj.lineItem[0].priceComponent:
            if price_component.type == self._TEST_LINE_ITEM_BASE_PRICE_COMPONENT_TYPE:
                self.verify_price_component(price_component, self._TEST_LiNE_ITEM_QUANTITY,
                                            self._TEST_LINE_ITEM_UNIT_PRICE * self._TEST_LiNE_ITEM_QUANTITY,
                                            self._TEST_LINE_ITEM_BASE_PRICE_COMPONENT_TYPE)
            elif price_component.type == self._TEST_LINE_ITEM_DISCOUNT_COMPONENT_TYPE:
                self.verify_price_component(price_component, self._TEST_LINE_ITEM_DISCOUNT,
                                            -self._TEST_LINE_ITEM_UNIT_PRICE * self._TEST_LiNE_ITEM_QUANTITY * (
                                                self._TEST_LINE_ITEM_DISCOUNT),
                                            self._TEST_LINE_ITEM_DISCOUNT_COMPONENT_TYPE)
            elif price_component.type == self._TEST_LINE_ITEM_DEDUCTION_PRICE_COMPONENT_TYPE:
                self.verify_price_component(price_component, self._TEST_LINE_ITEM_DEDUCTION_FACTOR,
                                            -self._TEST_LINE_ITEM_DEDUCTION,
                                            self._TEST_LINE_ITEM_DEDUCTION_PRICE_COMPONENT_TYPE)
            elif price_component.type == self._TEST_LINE_ITEM_TAX_PRICE_COMPONENT_TYPE:
                self.verify_price_component(price_component, self._TEST_LINE_ITEM_TAX_RATE,
                                            ((self._TEST_LINE_ITEM_UNIT_PRICE * self._TEST_LiNE_ITEM_QUANTITY * (
                                                    1 - self._TEST_LINE_ITEM_DISCOUNT))
                                             - self._TEST_LINE_ITEM_DEDUCTION) * self._TEST_LINE_ITEM_TAX_RATE,
                                            self._TEST_LINE_ITEM_TAX_PRICE_COMPONENT_TYPE)

    def verify_price_component(self, price_component, expected_factor, expected_amount, expected_type):
        self.assertGreater(len(price_component.extension), 0)
        self.assertEqual(price_component.extension[0].valueMoney.currency, self._TEST_INVOICE_CURRENCY)
        self.assertEqual(price_component.extension[0].valueMoney.value, self._TEST_LINE_ITEM_UNIT_PRICE)
        if expected_type:
            self.assertEqual(price_component.type, expected_type)
        self.assertEqual(float(price_component.factor), expected_factor, 1e-10)
        self.assertEqual(float(price_component.amount.value), expected_amount, 1e-10)
