from copy import deepcopy

from api_fhir_r4.converters import SubscriptionConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.models import Subscription
from api_fhir_r4.serializers import BaseFHIRSerializer
from api_fhir_r4.services import SubscriptionService
from api_fhir_r4.utils import TimeUtils


class SubscriptionSerializer(BaseFHIRSerializer):
    fhirConverter = SubscriptionConverter

    def to_internal_value(self, data):
        data['end'] = TimeUtils.str_iso_to_date(data['end'])
        return super().to_internal_value(data)

    def create(self, validated_data):
        user = self.context['request'].user
        service = SubscriptionService(user)
        copied_data = deepcopy(validated_data)
        del copied_data['_state'], copied_data['_original_state']
        result = service.create(copied_data)
        if result.get('success', False):
            return Subscription.objects.get(id=result['data']['id'])
        else:
            msg = result.get('message', 'Unknown')
            raise FHIRException(f'Error while creating a subscription: {msg}')

    def update(self, instance, validated_data):
        if str(instance.id) != validated_data['id']:
            raise FHIRException(f'Error while updating a subscription: You cannot change the instance ID')

        user = self.context['request'].user
        service = SubscriptionService(user)
        copied_data = {key: value for key, value in deepcopy(validated_data).items() if value is not None}
        del copied_data['_state'], copied_data['_original_state']
        result = service.update(copied_data)
        if result.get('success', False):
            return Subscription.objects.get(id=result['data']['id'])
        else:
            msg = result.get('message', 'Unknown')
            raise FHIRException(f'Error while updating a subscription: {msg}')
