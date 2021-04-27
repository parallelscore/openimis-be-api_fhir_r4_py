from django.utils.translation import gettext
from api_fhir_r4.configurations import R4CoverageConfig
from api_fhir_r4.converters import BaseFHIRConverter, ReferenceConverterMixin
from api_fhir_r4.models import Contract, Money, Period,\
     ContractTermAssetContext, ContractTermAssetValuedItem,  ContractTerm, ContractTermAsset,ContractSigner
from product.models import Product
from policy.models import Policy
from insuree.models import Insuree
from insuree.models import Family
from core.models import Officer
from api_fhir_r4.utils import DbManagerUtils,TimeUtils


class ContractConverter(BaseFHIRConverter, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_policy):
        fhir_contract = Contract()
        cls.build_contract_identifier(fhir_contract, imis_policy)
        contractTerm = ContractTerm()
        contractTermAsset = ContractTermAsset()
        cls.build_contract_asset_context(contractTermAsset, imis_policy)
        cls.build_contract_valued_item(contractTermAsset, imis_policy)
        cls.build_contract_valued_item_entity(contractTermAsset, imis_policy)
        cls.build_contract_asset_use_period(contractTermAsset, imis_policy)
        contractTerm.asset = [contractTermAsset]
        fhir_contract.term = [contractTerm]
        cls.build_contract_status(fhir_contract, imis_policy)
        cls.build_contract_signer(fhir_contract, imis_policy)
        cls.build_contract_state(fhir_contract, imis_policy)
        return fhir_contract
    
    @classmethod
    def to_imis_obj(cls,fhir_contract, audit_user_id):
        errors = []
        imis_policy = Policy()
        imis_policy.audit_user_id = audit_user_id
        cls.build_imis_period(imis_policy,fhir_contract.term,errors)
        cls.build_imis_useperiod(imis_policy,fhir_contract.term,errors)
        cls.build_imis_status(fhir_contract,imis_policy,errors)
        cls.build_imis_signer(fhir_contract,imis_policy,errors)
        cls.build_imis_product(fhir_contract,imis_policy,errors)
        cls.build_imis_state(fhir_contract,imis_policy,errors)
        cls.build_imis_insurees(fhir_contract,imis_policy,errors)
        cls.check_errors(errors)
        return imis_policy
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
    def build_contract_valued_item(cls, contract_asset, imis_policy):
        valued_item = ContractTermAssetValuedItem()
        policy_value = Money()
        policy_value.value = imis_policy.value
        valued_item.net = policy_value
        contract_asset.valuedItem.append(valued_item)
        return contract_asset

    @classmethod
    def build_contract_asset_use_period(cls, contract_asset, imis_policy):
        period_use = Period()
        period= Period()
        if imis_policy.start_date is not None:
            period.start = imis_policy.start_date.strftime("%Y-%m-%d")
            period_use.start = period.start
        if imis_policy.effective_date is not None:
            period_use.start = imis_policy.effective_date.strftime("%Y-%m-%d")
            if period_use.start is None:
                period.start = period_use.start
        if imis_policy.expiry_date is not None:
            period_use.end = imis_policy.expiry_date.strftime("%Y-%m-%d")
            period.end = period_use.end
            
        contract_asset.usePeriod = [period_use]
        contract_asset.period = [period]
        return contract_asset

    @classmethod
    def build_contract_asset_context(cls, contract_term_asset, imis_policy):
        insureePolicies = imis_policy.insuree_policies.all()
        for insureePolicy in insureePolicies:
            if insureePolicy.insuree.head is True:
                party_role = cls.build_simple_codeable_concept(R4CoverageConfig.get_offer_insuree_role_code())
            else:
                party_role = cls.build_simple_codeable_concept(R4CoverageConfig.get_offer_dependant_role_code())

            assetContext = ContractTermAssetContext()
            assetContext.code = [party_role]
            if imis_policy.family.location:
                display = insureePolicy.insuree.uuid + ":" + imis_policy.family.location.code
            else:
                display = insureePolicy.insuree.uuid
                
            assetContext.reference = cls.build_fhir_resource_reference(insureePolicy.insuree, "Patient",display)
            if contract_term_asset.context is None:
                contract_term_asset.context = [assetContext]
            else:
                contract_term_asset.context.append(assetContext)
        return contract_term_asset
        
    @classmethod
    def build_contract_status(cls, contract, imis_policy):
        if  imis_policy.status is imis_policy.STATUS_ACTIVE:
            contract.status = R4CoverageConfig.get_status_policy_code()
        elif  imis_policy.status is imis_policy.STATUS_IDLE:
            contract.status = R4CoverageConfig.get_status_offered_code()
        elif  imis_policy.status is imis_policy.STATUS_EXPIRED:
            contract.status = R4CoverageConfig.get_status_terminated_code()
        elif  imis_policy.status is imis_policy.STATUS_SUSPENDED:
            contract.status = R4CoverageConfig.get_status_disputed_code()
        else:
            contract.status = imis_policy.status
        return contract

    @classmethod
    def build_contract_state(cls, contract, imis_policy):
        if  imis_policy.stage is imis_policy.STAGE_NEW:
            contract.legalState = cls.build_simple_codeable_concept(R4CoverageConfig.get_status_offered_code())
        elif  imis_policy.stage is imis_policy.STAGE_RENEWED:
            contract.legalState = cls.build_simple_codeable_concept(R4CoverageConfig.get_status_renewed_code())
        else:
            contract.legalState = cls.build_simple_codeable_concept(imis_policy.stage)
        return contract

    @classmethod
    def build_contract_valued_item_entity(cls, contract_asset, imis_policy):
        valued_item = ContractTermAssetValuedItem()
        typeReference = cls.build_fhir_resource_reference(imis_policy.product, "InsuranceProduct", imis_policy.product.code )
        valued_item.entityReference=typeReference
        contract_asset.valuedItem.append(valued_item)
        return contract_asset

    @classmethod
    def build_contract_signer(cls, contract, imis_policy):
        if imis_policy.officer is not None:
            reference = cls.build_fhir_resource_reference(imis_policy.officer, "Practitioner")
            signer = ContractSigner()
            signer.party = reference
            eo_type = cls.build_simple_codeable_concept(R4CoverageConfig.get_signer_eo_type_code())
            signer.type = eo_type
            if contract.signer is None:
                contract.signer = signer
            else :
                contract.signer.append(signer)
        if imis_policy.family is not None:
            if imis_policy.family.head_insuree is not None:
                reference = cls.build_fhir_resource_reference(imis_policy.family.head_insuree, "Patient")
                signer = ContractSigner()
                signer.party = reference
                eo_type = cls.build_simple_codeable_concept(R4CoverageConfig.get_signer_head_type_code())
                signer.type = eo_type
                if contract.signer is None:
                    contract.signer = signer
                else :
                    contract.signer.append(signer)            

    @classmethod
    def build_imis_period(cls, imis_policy,fhir_contract,errors):
        for term in  fhir_contract:
            if term.asset:
                for asset in term.asset:
                    if asset.period:
                        for period in asset.period:
                            if not cls.valid_condition(period.start is None, gettext('Missing  `period start` attribute'),errors):
                                imis_policy.start_date = TimeUtils.str_to_date(period.start) 
                                imis_policy.enroll_date = TimeUtils.str_to_date(period.start) 
                            if not cls.valid_condition(period.end is None, gettext('Missing  `period end` attribute'),errors):
                                imis_policy.expiry_date = TimeUtils.str_to_date(period.end) 
                                imis_policy.validity_to = TimeUtils.str_to_date(period.end)
                    else:
                        cls.valid_condition(not asset.period, gettext('Missing  `period` attribute'),errors)
                        
                        
    @classmethod
    def build_imis_useperiod(cls, imis_policy,fhir_contract,errors):
        for term in  fhir_contract:
            if term.asset:
                for asset in term.asset:
                    if asset.usePeriod:
                        for period in asset.usePeriod:
                            if not cls.valid_condition(period.start is None, gettext('Missing  `usePeriod start` attribute'),errors):
                                imis_policy.effective_date = TimeUtils.str_to_date(period.start)
                            if not cls.valid_condition(period.end is None, gettext('Missing  `usePeriod end` attribute'),errors):
                                imis_policy.expiry_date = TimeUtils.str_to_date(period.end) 
                    else:
                        cls.valid_condition(not asset.usePeriod, gettext('Missing  `usePeriod` attribute'),errors)
    
    @classmethod
    def build_imis_status(cls, fhir_contract, imis_policy,errors):
        if fhir_contract.status:
            imis_policy.status = fhir_contract.status
        else:
            cls.valid_condition(fhir_contract.status is None, gettext('Missing  `status` attribute'),errors)

    @classmethod
    def build_imis_signer(cls,fhir_contract, imis_policy,errors):
        if fhir_contract.signer:
            for signer in  fhir_contract.signer:
                if signer.type:
                    if signer.type.text and signer.party.reference is not None:
                        if signer.type.text =='HeadOfFamily':
                            reference = signer.party.reference.split("/", 2)
                            
                            try:
                                insuree = Insuree.objects.get(uuid=reference[1])
                                if insuree.head:
                                    imis_policy.family= Family.objects.filter(head_insuree=insuree).first()
                                else:
                                    cls.valid_condition(True, gettext('Missing  `Member details provided belong to a depedant` attribute'),errors)
                            except:
                                cls.valid_condition(True, gettext('Missing  `Family head provided does not exist` attribute'),errors)
                        elif signer.type.text == 'EnrolmentOfficer':
                            reference = signer.party.reference.split("/", 2)
                            imis_policy.officer = Officer.objects.get(uuid=reference[1])
                        else:
                            pass     
                else:
                    cls.valid_condition(signer.type is None, gettext('Missing  `type` attribute'),errors)
        else:
            cls.valid_condition(not fhir_contract.signer, gettext('Missing  `signer` attribute'),errors)
            
    @classmethod
    def build_imis_insurees(cls,fhir_contract,imis_policy,errors):
        if fhir_contract.term:
            insurees =[]
            for term in  fhir_contract.term:
                if term.asset:
                    for asset in term.asset:
                        if asset.context:
                            for item in asset.context:
                               if item.reference is not None:
                                   reference = item.reference.reference.split("/", 2)
                                   obj = Insuree.objects.get(uuid=reference[1])
                                   if imis_policy.family_id is not None:
                                       if obj.family == imis_policy.family:
                                            insurees.append(obj.uuid)
                                       else:
                                            if 'Missing  `Invalid Context reference` attribute' not in errors:
                                                cls.valid_condition(True, gettext('Missing  `Invalid Context reference` attribute'),errors)
                            imis_policy.insurees = insurees                    
                        else:
                            cls.valid_condition(not asset.context, gettext('Missing  `context` attribute'),errors)
                else:
                    cls.valid_condition(not term.asset, gettext('Missing  `asset` attribute'),errors)
                        
        else:
            cls.valid_condition(not fhir_contract, gettext('Missing  `term` attribute'),errors)
            
    
    
    @classmethod
    def build_imis_product(cls,fhir_contract,imis_policy,errors):
        if fhir_contract.term:
            for term in  fhir_contract.term:
                if term.asset:
                    for asset in term.asset:
                        if asset.valuedItem:
                            for item in asset.valuedItem:
                                if item.entityReference is not None:
                                    if item.entityReference.reference is not None:
                                        reference = item.entityReference.reference.split("/", 2)
                                        imis_policy.product = Product.objects.get(uuid=reference[1])
                                if item.net is not None:
                                    if item.net.value is not None:
                                        imis_policy.value = item.net.value                                                       
                        else:
                            cls.valid_condition(not asset.valuedItem, gettext('Missing  `valuedItem` attribute'),errors)
                else:
                    cls.valid_condition(not term.asset, gettext('Missing  `asset` attribute'),errors)
                        
        else:
            cls.valid_condition(not fhir_contract, gettext('Missing  `term` attribute'),errors)
            
                
    @classmethod
    def build_imis_state(cls,fhir_contract, imis_policy,errors):
        if fhir_contract.legalState:
            if fhir_contract.legalState.text:
                if fhir_contract.legalState.text == 'N' or fhir_contract.legalState == 'R':
                    imis_policy.stage = fhir_contract.legalState.text
                else:
                    cls.valid_condition(True, gettext('Missing  `invalid legalState` attribute'),errors)
                    
        else:
            cls.valid_condition(fhir_contract.legalState is None, gettext('Missing  `legalState` attribute'),errors)