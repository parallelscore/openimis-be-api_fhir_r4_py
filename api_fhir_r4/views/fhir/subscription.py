from rest_framework.viewsets import ModelViewSet

from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.models import Subscription
from api_fhir_r4.serializers import SubscriptionSerializer
from api_fhir_r4.services import SubscriptionService
from api_fhir_r4.views.fhir.base import BaseFHIRView


class SubscriptionViewSet(BaseFHIRView, ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.filter(is_deleted=False).order_by('date_created')
    http_method_names = ('get', 'post', 'put', 'delete')

    def perform_destroy(self, instance):
        service = SubscriptionService(self.request.user)
        result = service.delete({'id': instance.id})
        if not result.get('success', False):
            msg = result.get('message', 'Unknown')
            raise FHIRException(f'Error while deleting a subscription: {msg}')
