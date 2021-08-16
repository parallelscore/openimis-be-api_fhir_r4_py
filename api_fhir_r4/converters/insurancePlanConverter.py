from django.utils.translation import gettext as _
from product.models import Product
from api_fhir_r4.configurations import R4IdentifierConfig
from api_fhir_r4.converters import BaseFHIRConverter, ReferenceConverterMixin
from fhir.resources.insuranceplan import InsurancePlan
from fhir.resources.period import Period
from fhir.resources.reference import Reference
from api_fhir_r4.utils import DbManagerUtils, TimeUtils


class InsurancePlanConverter(BaseFHIRConverter, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_product, reference_type=ReferenceConverterMixin.UUID_REFERENCE_TYPE):
        fhir_insurance_plan = InsurancePlan.construct()
        # then create fhir object as usual
        cls.build_fhir_identifiers(fhir_insurance_plan, imis_product)
        cls.build_fhir_pk(fhir_insurance_plan, imis_product.uuid)
        cls.build_fhir_name(fhir_insurance_plan, imis_product)
        cls.build_fhir_type(fhir_insurance_plan, imis_product)
        cls.build_fhir_period(fhir_insurance_plan, imis_product)
        return fhir_insurance_plan

    @classmethod
    def to_imis_obj(cls, fhir_insurance_plan, audit_user_id):
        errors = []
        fhir_insurance_plan = InsurancePlan(**fhir_insurance_plan)
        imis_product = Product()
        imis_product.uuid = None
        imis_product.audit_user_id = audit_user_id
        cls.check_errors(errors)
        return imis_product

    @classmethod
    def get_reference_obj_id(cls, imis_product):
        return imis_product.uuid

    @classmethod
    def get_fhir_resource_type(cls):
        return InsurancePlan

    @classmethod
    def get_imis_obj_by_fhir_reference(cls, reference, errors=None):
        imis_insurance_uuid = cls.get_resource_id_from_reference(reference)
        return DbManagerUtils.get_object_or_none(Product, uuid=imis_insurance_uuid)

    @classmethod
    def build_fhir_identifiers(cls, fhir_insurance_plan, imis_product):
        identifiers = []
        cls.build_fhir_uuid_identifier(identifiers, imis_product)
        cls.build_fhir_code_identifier(identifiers, imis_product)
        fhir_insurance_plan.identifier = identifiers

    @classmethod
    def build_imis_identifiers(cls, imis_product, fhir_insurance_plan):
        value = cls.get_fhir_identifier_by_code(fhir_insurance_plan.identifier,
                                                R4IdentifierConfig.get_fhir_item_code_type())
        if value:
            imis_product.code = value

    @classmethod
    def get_fhir_code_identifier_type(cls):
        return R4IdentifierConfig.get_fhir_item_code_type()

    @classmethod
    def build_fhir_name(cls, fhir_insurance_plan, imis_product):
        if imis_product.name and imis_product.name != "":
            fhir_insurance_plan.name = imis_product.name

    @classmethod
    def build_imis_name(cls, imis_product, fhir_insurance_plan):
        if fhir_insurance_plan.name and fhir_insurance_plan.name != "":
            imis_product.name = fhir_insurance_plan.name

    @classmethod
    def build_fhir_type(cls, fhir_insurance_plan, imis_product):
        type = cls.build_codeable_concept(
            code="medical",
            system="http://terminology.hl7.org/CodeSystem/insurance-plan-type"
        )
        if len(type.coding) == 1:
            type.coding[0].display = _("Medical")
        fhir_insurance_plan.type = [type]

    @classmethod
    def build_fhir_period(cls, fhir_insurance_plan, imis_product):
        from core import datetime
        period = Period.construct()
        if imis_product.date_from:
            # check if datetime object
            if isinstance(imis_product.date_from, datetime.datetime):
                period.start = str(imis_product.date_from.date().isoformat())
            else:
                period.start = str(imis_product.date_from.isoformat())
        if imis_product.date_to:
            # check if datetime object
            if isinstance(imis_product.date_to, datetime.datetime):
                period.end = str(imis_product.date_to.date().isoformat())
            else:
                period.end = str(imis_product.date_to.isoformat())
        if period.start or period.end:
            fhir_insurance_plan.period = period

    @classmethod
    def build_imis_period(cls, imis_product, fhir_insurance_plan):
        if fhir_insurance_plan.period:
            period = fhir_insurance_plan.period
            if period.start:
                imis_product.date_from = TimeUtils.str_to_date(period.start)
            if period.end:
                imis_product.date_to = TimeUtils.str_to_date(period.end)

    @classmethod
    def build_fhir_extentions(cls, fhir_insurance_plan, imis_product, reference_type):
        pass

    @classmethod
    def build_imis_extentions(cls, imis_product, fhir_insurance_plan):
        pass
