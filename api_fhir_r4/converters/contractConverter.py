from api_fhir_r4.configurations import R4CoverageConfig
from api_fhir_r4.converters import BaseFHIRConverter, ReferenceConverterMixin
from api_fhir_r4.models import  Reference,  Contract, Money, Extension, Period,\
     ContractTermOfferParty, ContractTermAssetValuedItem,  ContractTerm, ContractTermAsset, ContractTermOffer,ContractSigner
from product.models import ProductItem, ProductService
from policy.models import Policy
from insuree.models import InsureePolicy
from api_fhir_r4.utils import DbManagerUtils


class ContractConverter(BaseFHIRConverter, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_policy):
        fhir_contract = Contract()
        cls.build_contract_identifier(fhir_contract, imis_policy)
        contractTerm = ContractTerm()
        cls.build_contract_offer_party(contractTerm, imis_policy)
        contractTermAsset = ContractTermAsset()
        cls.build_contract_valued_item(contractTermAsset, imis_policy)
        cls.build_contract_asset_type_reference(contractTermAsset, imis_policy)
        cls.build_contract_asset_use_period(contractTermAsset, imis_policy)
        contractTerm.asset = [contractTermAsset]
        fhir_contract.term = [contractTerm]
        cls.build_contract_status(fhir_contract, imis_policy)
        cls.build_contract_signer(fhir_contract, imis_policy)
        cls.build_contract_state(fhir_contract, imis_policy)
        return fhir_contract

    @classmethod
    def get_reference_obj_id(cls, imis_policy):
        return imis_policy.uuid

    @classmethod
    def get_fhir_resource_type(cls):
        return Contract

    @classmethod
    def get_imis_obj_by_fhir_reference(cls, reference, errors=None):
        imis_policy_code = cls.get_resource_id_from_reference(reference)
        return DbManagerUtils.get_object_or_none(Policy, code=imis_policy_code)

    @classmethod
    def build_contract_identifier(cls, fhir_contract, imis_policy):
        identifiers = []
        cls.build_fhir_uuid_identifier(identifiers, imis_policy)
        fhir_contract.identifier = identifiers
        return fhir_contract

 
    @classmethod
    def build_contract_valued_item(cls, contract_asset, imis_coverage):
        valued_item = ContractTermAssetValuedItem()
        policy_value = Money()
        policy_value.value = imis_coverage.value
        valued_item.net = policy_value
        contract_asset.valuedItem.append(valued_item)
        return contract_asset

    @classmethod
    def build_contract_asset_use_period(cls, contract_asset, imis_coverage):
        period_use = Period()
        period_use.start = imis_coverage.effective_date.strftime("%Y-%m-%d")
        period_use.end = imis_coverage.expiry_date.strftime("%Y-%m-%d")
        period= Period()
        period.start = imis_coverage.start_date.strftime("%Y-%m-%d")
        period.end = imis_coverage.expiry_date.strftime("%Y-%m-%d")
        contract_asset.usePeriod = [period_use]
        contract_asset.period = [period]
        return contract_asset

    @classmethod
    def build_contract_offer_party(cls, contract_term, imis_coverage):
        insureePolicies = imis_coverage.insuree_policies.filter(validity_to__isnull=True)
        offerParty = ContractTermOfferParty()
        offerParty.reference = []
        party_role = cls.build_simple_codeable_concept(R4CoverageConfig.get_offer_insuree_role_code())
        offerParty.role = party_role
        if contract_term.offer is None:
                contract_term.offer = ContractTermOffer()
        for insureePolicy in insureePolicies:
            reference = cls.build_fhir_resource_reference(insureePolicy.insuree, "Patient")
            offerParty.reference.append(reference)
        if len(offerParty.reference)>0:
            if contract_term.offer.party is None:
                contract_term.offer.party =[offerParty]
            else:
                contract_term.offer.party.append(offerParty)
        return contract_term
        
    @classmethod
    def build_contract_status(cls, contract, imis_coverage):
        if  imis_coverage.status is imis_coverage.STATUS_ACTIVE:
            contract.status = R4CoverageConfig.get_status_policy_code()
        elif  imis_coverage.status is imis_coverage.STATUS_IDLE:
            contract.status = R4CoverageConfig.get_status_offered_code()
        elif  imis_coverage.status is imis_coverage.STATUS_ACTIVE:
            contract.status = R4CoverageConfig.get_status_terminated_code()
        return contract

    @classmethod
    def build_contract_state(cls, contract, imis_coverage):
        if  imis_coverage.status is imis_coverage.STAGE_NEW:
            contract.state = R4CoverageConfig.get_status_offered_code()
        elif  imis_coverage.status is imis_coverage.STAGE_RENEWED:
            contract.state = R4CoverageConfig.get_status_renewed_code()
        return contract

    @classmethod
    def build_contract_asset_type_reference(cls, contract_asset, imis_coverage):
        typeReference = cls.build_fhir_resource_reference(imis_coverage.product, "InsurancePlan")
        contract_asset.typeReference = [typeReference]
        return contract_asset

    @classmethod
    def build_contract_signer(cls, contract, imis_coverage):
        if imis_coverage.officer is not None:
            reference = cls.build_fhir_resource_reference(imis_coverage.officer, "Practitioner")
            signer = ContractSigner()
            signer.party = reference
            eo_type = cls.build_simple_codeable_concept(R4CoverageConfig.get_signer_eo_type_code())
            signer.type = eo_type
            if contract.signer is None:
                contract.signer = signer
            else :
                contract.signer.append(signer)
        if imis_coverage.family is not None:
            if imis_coverage.family.head_insuree is not None:
                reference = cls.build_fhir_resource_reference(imis_coverage.family.head_insuree, "Patient")
                signer = ContractSigner()
                signer.party = reference
                eo_type = cls.build_simple_codeable_concept(R4CoverageConfig.get_signer_head_type_code())
                signer.type = eo_type
                if contract.signer is None:
                    contract.signer = signer
                else :
                    contract.signer.append(signer)            
