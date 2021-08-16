from product.models import Product
from api_fhir_r4.converters import BaseFHIRConverter, ReferenceConverterMixin
from fhir.resources.insuranceplan import InsurancePlan
from api_fhir_r4.utils import DbManagerUtils


class InsurancePlanConverter(BaseFHIRConverter, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_product, reference_type=ReferenceConverterMixin.UUID_REFERENCE_TYPE):
        fhir_insurance_plan = InsurancePlan.construct()
        # then create fhir object as usual
        cls.build_fhir_identifiers(fhir_insurance_plan, imis_product)
        cls.build_fhir_pk(fhir_insurance_plan, imis_product.uuid)
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
    def build_fhir_identifiers(cls, fhir_family, imis_family):
        identifiers = []
        cls.build_fhir_uuid_identifier(identifiers, imis_family)
        cls.build_fhir_code_identifier(identifiers, imis_family)
        fhir_family.identifier = identifiers

    @classmethod
    def build_fhir_code_identifier(cls, identifiers, imis_product):
        pass

    @classmethod
    def build_imis_identifiers(cls, imis_product, identifier):
        pass

    @classmethod
    def build_fhir_extentions(cls, fhir_insurance_plan, imis_product, reference_type):
        pass

    @classmethod
    def build_imis_extentions(cls, imis_product, fhir_insurance_plan):
        pass
