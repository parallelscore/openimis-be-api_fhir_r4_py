from claim.models import Claim

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.permissions import FHIRApiClaimPermissions
from api_fhir_r4.serializers import ClaimResponseSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class ClaimResponseViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet,
                           mixins.UpdateModelMixin):
    lookup_field = 'uuid'
    serializer_class = ClaimResponseSerializer
    permission_classes = (FHIRApiClaimPermissions,)

    def get_queryset(self):
        return Claim.get_queryset(None, self.request.user)
