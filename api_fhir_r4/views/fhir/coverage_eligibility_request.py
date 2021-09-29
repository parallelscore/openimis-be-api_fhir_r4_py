from insuree.models import Insuree

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.configurations import R4CoverageEligibilityConfiguration as Config
from api_fhir_r4.permissions import FHIRApiCoverageEligibilityRequestPermissions
from api_fhir_r4.serializers import CoverageEligibilityRequestSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class CoverageEligibilityRequestViewSet(BaseFHIRView, mixins.CreateModelMixin, GenericViewSet):
    queryset = Insuree.filter_queryset()
    serializer_class = CoverageEligibilityRequestSerializer
    permission_classes = (FHIRApiCoverageEligibilityRequestPermissions,)

    def get_queryset(self):
        return Insuree.get_queryset(None, self.request.user)
