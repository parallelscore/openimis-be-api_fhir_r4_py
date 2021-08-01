from location.models import HealthFacility
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.permissions import FHIRApiHealthServicePermissions
from api_fhir_r4.serializers import HealthcareServiceSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class HealthcareServiceViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = HealthcareServiceSerializer
    permission_classes = (FHIRApiHealthServicePermissions,)

    def get_queryset(self):
        return HealthFacility.get_queryset(None, self.request.user)
