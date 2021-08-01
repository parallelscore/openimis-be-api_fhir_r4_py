from claim.models import ClaimAdmin

from rest_framework import viewsets

from api_fhir_r4.permissions import FHIRApiPractitionerPermissions
from api_fhir_r4.serializers import PractitionerSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class PractitionerViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = PractitionerSerializer
    permission_classes = (FHIRApiPractitionerPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        identifier = request.GET.get("identifier")
        if identifier:
            queryset = queryset.filter(code=identifier)
        serializer = PractitionerSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return ClaimAdmin.get_queryset(None, self.request.user)
