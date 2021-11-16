from fhir.resources.extension import Extension
from api_fhir_r4.configurations import GeneralConfiguration, R4IdentifierConfig
from api_fhir_r4.converters import BaseFHIRConverter, ReferenceConverterMixin
from fhir.resources.invoice import Invoice as FHIRInvoice, \
    InvoiceLineItem as FHIRInvoiceLineItem, InvoiceLineItemPriceComponent
from fhir.resources.money import Money
from api_fhir_r4.mapping.invoiceMapping import ChargeItemMapping, InvoiceTypeMapping


class InvoiceConverter(BaseFHIRConverter, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_invoice, reference_type=ReferenceConverterMixin.UUID_REFERENCE_TYPE):
        fhir_invoice = {"status": "active"}
        fhir_invoice = FHIRInvoice(**fhir_invoice)
        # then create fhir object as usual
        cls.build_fhir_identifiers(fhir_invoice, imis_invoice)
        cls.build_fhir_pk(fhir_invoice, imis_invoice.id)
        cls.build_fhir_type(fhir_invoice, imis_invoice)
        cls.build_fhir_date(fhir_invoice, imis_invoice)
        cls.build_fhir_totals(fhir_invoice, imis_invoice)
        cls.build_fhir_line_items(fhir_invoice, imis_invoice.line_items, imis_invoice.currency_code)
        return fhir_invoice

    @classmethod
    def get_fhir_code_identifier_type(cls):
        return R4IdentifierConfig.get_fhir_generic_type_code()

    @classmethod
    def build_fhir_identifiers(cls, fhir_invoice, imis_invoice):
        identifiers = []
        cls.build_fhir_uuid_identifier(identifiers, imis_invoice)
        cls.build_fhir_code_identifier(identifiers, imis_invoice)
        fhir_invoice.identifier = identifiers

    @classmethod
    def build_fhir_type(cls, fhir_invoice, imis_invoice):
        invoice_type = InvoiceTypeMapping.invoice_type[imis_invoice.subject_type.model]
        fhir_invoice.type = cls.build_codeable_concept(
            code=invoice_type["code"],
            display=invoice_type["display"],
            system=f"{GeneralConfiguration.get_system_base_url()}/CodeSystem/invoice-type",
        )

    @classmethod
    def build_fhir_date(cls, fhir_invoice, imis_invoice):
        fhir_invoice.date = imis_invoice.date_invoice

    @classmethod
    def build_fhir_totals(cls, fhir_invoice, imis_invoice):
        fhir_invoice.totalNet = cls.build_fhir_invoice_money(imis_invoice.amount_net, imis_invoice.currency_code)
        fhir_invoice.totalGross = cls.build_fhir_invoice_money(imis_invoice.amount_total, imis_invoice.currency_code)

    @classmethod
    def build_fhir_invoice_money(cls, imis_total_value, imis_currency):
        total = Money.construct()
        total.value = imis_total_value
        total.currency = imis_currency
        return total

    @classmethod
    def build_fhir_line_items(cls, fhir_invoice, imis_line_items, currency):
        fhir_invoice.lineItem = []
        for line in imis_line_items.all():
            fhir_line_item = FHIRInvoiceLineItem.construct()
            cls.build_line_item_charge_item_codeable_concept(fhir_line_item, line)
            cls.build_line_item_price_component_base(fhir_line_item, line, currency)
            fhir_invoice.lineItem.append(fhir_line_item)

    @classmethod
    def build_line_item_charge_item_codeable_concept(cls, fhir_line_item, line_item):
        charge_item = ChargeItemMapping.charge_item[line_item.line_type.model]
        type = cls.build_codeable_concept(
            code=charge_item['code'],
            display=charge_item['display'],
            system=f"{GeneralConfiguration.get_system_base_url()}/CodeSystem/invoice-charge-item",
        )
        fhir_line_item.chargeItemCodeableConcept = type

    @classmethod
    def build_line_item_price_component_base(cls, fhir_line_item, line, currency):
        fhir_line_item.priceComponent = []
        price_component = {"type": "base"}
        price_component = InvoiceLineItemPriceComponent(**price_component)
        price_component.extension = []

        extension = Extension.construct()
        extension.url = f"{GeneralConfiguration.get_system_base_url()}/StructureDefinition/unit-price"
        unit_price = Money.construct()
        unit_price.value = line.unit_price
        unit_price.currency = currency
        extension.valueMoney = unit_price
        price_component.extension.append(extension)

        price_component.type = 'base'
        price_component.code = cls.build_codeable_concept(
            code="Code",
            display=line.code,
            system="Code"
        )
        price_component.factor = line.quantity
        price_component.amount = cls.build_fhir_invoice_money(line.unit_price*line.quantity, currency)
        fhir_line_item.priceComponent.append(price_component)
