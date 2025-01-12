from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin, MultiIdentifierUpdateMixin
from api_fhir_r4.model_retrievers import UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiActivityDefinitionPermissions
from api_fhir_r4.serializers import ActivityDefinitionSerializer
from api_fhir_r4.views.fhir.base import BaseFHIRView
from api_fhir_r4.views.filters import ValidityFromRequestParameterFilter
from medical.models import Service


class ActivityDefinitionViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, MultiIdentifierUpdateMixin, viewsets.ModelViewSet):
    # class ActivityDefinitionViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, mixins.ListModelMixin, GenericViewSet):
    # This above signature allows for fetching ActivityDefinition only without creatig/Updating
    retrievers = [UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever]
    serializer_class = ActivityDefinitionSerializer
    permission_classes = (FHIRApiActivityDefinitionPermissions,)

    def get_queryset(self):
        queryset = Service.get_queryset(None, self.request.user)
        return ValidityFromRequestParameterFilter(self.request).filter_queryset(queryset)
