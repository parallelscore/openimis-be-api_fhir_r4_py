from rest_framework.viewsets import ModelViewSet

from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.models import Subscription
from api_fhir_r4.permissions import FHIRApiSubscriptionPermissions
from api_fhir_r4.serializers import SubscriptionSerializer
from api_fhir_r4.services import SubscriptionService
from api_fhir_r4.views.fhir.base import BaseFHIRView


class SubscriptionViewSet(BaseFHIRView, ModelViewSet):
    _error_while_saving = 'Error while saving a subscription: %(msg)s'
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.filter(is_deleted=False).order_by('date_created')
    http_method_names = ('get', 'post', 'put', 'delete')
    permission_classes = (FHIRApiSubscriptionPermissions,)

    def perform_destroy(self, instance):
        self.check_object_owner(self.request.user, instance)
        service = SubscriptionService(self.request.user)
        result = service.delete({'id': instance.id})
        self.check_error_message(result)

    @staticmethod
    def check_error_message(result):
        if not result.get('success', False):
            msg = result.get('message', 'Unknown')
            raise FHIRException(f'Error while deleting a subscription: {msg}')

    def check_object_owner(self, user, instance):
        if str(user.id).lower() != str(instance.user_created.id).lower():
            raise FHIRException(self._error_while_saving % {'msg': 'You are not the owner of this subscription'})
