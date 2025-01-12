import copy
import uuid

from medical.models import Item
from medical.services import MedicationItemService
from api_fhir_r4.converters import MedicationConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class MedicationSerializer(BaseFHIRSerializer):
    fhirConverter = MedicationConverter()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        code = validated_data.get('code')
        
        if Item.objects.filter(code=code).count() > 0:
            raise FHIRException(
                'Exists medical item with following code `{}`'.format(code))

        if 'uuid' in validated_data.keys() and validated_data.get('uuid') is None:
            # In serializers using graphql services can't provide uuid. If uuid is provided then
            # resource is updated and not created. This check ensure UUID was provided.
            validated_data['uuid'] = uuid.uuid4()

        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        del copied_data['uuid']
        # return Item.objects.create(**copied_data)
        return MedicationItemService(user).create_or_update(copied_data, Item)

    def update(self, instance, validated_data):
        request = self.context.get("request")

        user = request.user

        instance.code = validated_data.get('code', instance.code)
        instance.name = validated_data.get('name', instance.name)
        instance.package = validated_data.get('package', instance.package)
        instance.price = validated_data.get('price', instance.price)
        instance.type = validated_data.get('type', instance.type)
        instance.care_type = validated_data.get(
            'care_type', instance.care_type)
        instance.frequency = validated_data.get(
            'frequency', instance.frequency)
        instance.patient_category = validated_data.get(
            'patient_category', instance.patient_category)
        instance.audit_user_id = self.get_audit_user_id()
        # instance.save()
        return MedicationItemService(user).create_or_update(instance.__dict__, Item)
