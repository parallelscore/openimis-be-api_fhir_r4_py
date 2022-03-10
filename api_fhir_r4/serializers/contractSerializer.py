from api_fhir_r4.converters.contractConverter import ContractConverter
from api_fhir_r4.configurations import R4CoverageConfig
from api_fhir_r4.serializers import BaseFHIRSerializer
from payment.services import match_payment
from policy.models import Policy
from insuree.models import InsureePolicy,Insuree
import copy
from api_fhir_r4.exceptions import FHIRException


class ContractSerializer(BaseFHIRSerializer):
    fhirConverter = ContractConverter

    def create(self,validated_data):
        family = validated_data.get('family_id')
        insurees = validated_data.pop('insurees')
        premiums = validated_data.pop('contributions')

        if Policy.objects.filter(family_id=family).filter(start_date__range=[validated_data.get('effective_date'),validated_data.get('expiry_date')]).count() > 0:
            raise FHIRException('Contract exists for this patient')

        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        policy = Policy.objects.create(**copied_data)

        for patient in insurees:
            insuree = Insuree.objects.get(uuid=patient)
            InsureePolicy.objects.create(
                policy=policy,
                insuree=insuree,
                start_date=policy.start_date,
                effective_date=policy.effective_date,
                expiry_date=policy.expiry_date,
                enrollment_date=policy.enroll_date,
                validity_to=policy.expiry_date
            )

        # create contributions related to newly created policy
        if premiums:
            for premium in premiums:
                premium.policy = policy
                premium.audit_user_id = copied_data['audit_user_id']
                premium.save()

            sum_premiums = policy.sum_premiums()
            if sum_premiums >= policy.value:
                policy.save_history()
                policy.status = Policy.STATUS_ACTIVE
                policy.save()

        return policy
    
    def update(self, instance, validated_data):
        instance.save()
        return instance
