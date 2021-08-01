from medical.models import Service
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.permissions import FHIRApiActivityDefinitionPermissions
from api_fhir_r4.serializers import ActivityDefinitionSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class ActivityDefinitionViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = ActivityDefinitionSerializer
    permission_classes = (FHIRApiActivityDefinitionPermissions,)

    def get_queryset(self):
        return Service.get_queryset(None, self.request.user)
