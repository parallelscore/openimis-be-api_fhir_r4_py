from api_fhir_r4.converters.contractConverter import ContractConverter
from api_fhir_r4.serializers import BaseFHIRSerializer
from policy.models import Policy
from insuree.models import InsureePolicy,Insuree
import copy
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.utils import TimeUtils

class ContractSerializer(BaseFHIRSerializer):
    fhirConverter = ContractConverter
    def create(self,validated_data):
        family = validated_data.get('family_id')
        insurees = validated_data.pop('insurees')
        if Policy.objects.filter(family_id=family).filter(expiry_date__gte=TimeUtils.now().strftime("%Y-%m-%d")).count() > 0:
            raise FHIRException('Contract exists for this patient')
        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        obj=Policy.objects.create(**copied_data)
        for patient in insurees:
            insuree = Insuree.objects.get(uuid=patient)
            InsureePolicy.objects.create(policy=obj,insuree=insuree,start_date=obj.start_date,effective_date=obj.effective_date,expiry_date=obj.expiry_date,enrollment_date=obj.enroll_date,validity_to=obj.expiry_date)
        return obj
    
    def update(self, instance, validated_data):
        instance.save()
        return instance