from claim.models import Feedback

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.permissions import FHIRApiCommunicationRequestPermissions
from api_fhir_r4.serializers import CommunicationRequestSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class CommunicationRequestViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = CommunicationRequestSerializer
    permission_classes = (FHIRApiCommunicationRequestPermissions,)

    def get_queryset(self):
        return Feedback.get_queryset(None, self.request.user)
