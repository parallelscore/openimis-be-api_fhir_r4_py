from medical.models import Diagnosis
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin
from api_fhir_r4.model_retrievers import DatabaseIdentifierModelRetriever, CodeIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiConditionPermissions
from api_fhir_r4.serializers import ConditionSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class ConditionViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin,
                       mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    retrievers = [DatabaseIdentifierModelRetriever, CodeIdentifierModelRetriever]
    serializer_class = ConditionSerializer
    permission_classes = (FHIRApiConditionPermissions,)

    def get_queryset(self):
        return Diagnosis.get_queryset(None, self.request.user)
