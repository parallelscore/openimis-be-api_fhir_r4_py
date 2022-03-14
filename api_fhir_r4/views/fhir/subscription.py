from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.viewsets import ModelViewSet

from api_fhir_r4.models import Subscription
from api_fhir_r4.permissions import FHIRApiSubscriptionPermissions
from api_fhir_r4.serializers import SubscriptionSerializer
from api_fhir_r4.services import SubscriptionService
from api_fhir_r4.views.fhir.base import BaseFHIRView


class SubscriptionViewSet(BaseFHIRView, ModelViewSet):
    _error_while_deleting = 'Error while deleting a subscription: %(msg)s'
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.filter(is_deleted=False).order_by('date_created')
    http_method_names = ('get', 'post', 'put', 'delete')
    permission_classes = (FHIRApiSubscriptionPermissions,)

    def perform_destroy(self, instance):
        if not self.check_if_owner(self.request.user, instance):
            raise PermissionDenied(
                detail=self._error_while_deleting % {'msg': 'You are not the owner of this subscription'})
        service = SubscriptionService(self.request.user)
        result = service.delete({'id': instance.id})
        self.check_error_message(result)

    @staticmethod
    def check_error_message(result):
        if not result.get('success', False):
            msg = result.get('message', 'Unknown')
            raise APIException(f'Error while deleting a subscription: {msg}')

    @staticmethod
    def check_if_owner(user, instance):
        return str(user.id).lower() == str(instance.user_created.id).lower()

