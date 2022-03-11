from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.models import Subscription
from api_fhir_r4.openapi_schema_extensions import get_inline_error_serializer
from api_fhir_r4.serializers import SubscriptionSerializer
from api_fhir_r4.serializers.subscriptionSerializer import SubscriptionSerializerSchema
from api_fhir_r4.services import SubscriptionService
from api_fhir_r4.views.fhir.base import BaseFHIRView


@extend_schema_view(
    list=extend_schema(responses={(200, 'application/json'): SubscriptionSerializerSchema()}),
    retrieve=extend_schema(responses={
        (200, 'application/json'): SubscriptionSerializerSchema(),
        (404, 'application/json'): get_inline_error_serializer()
    }),
    create=extend_schema(
        request=SubscriptionSerializerSchema(),
        responses={(201, 'application/json'): SubscriptionSerializerSchema()}
    ),
    update=extend_schema(
        request=SubscriptionSerializerSchema(),
        responses={(200, 'application/json'): SubscriptionSerializerSchema()}
    ),
    destroy=extend_schema(responses={204: None})
)
class SubscriptionViewSet(BaseFHIRView, ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.filter(is_deleted=False).order_by('date_created')
    http_method_names = ('get', 'post', 'put', 'delete')

    def perform_destroy(self, instance):
        service = SubscriptionService(self.request.user)
        result = service.delete({'id': instance.uuid})
        if not result.get('success', False):
            msg = result.get('message', 'Unknown')
            raise FHIRException(f'Error while deleting a subscription: {msg}')
