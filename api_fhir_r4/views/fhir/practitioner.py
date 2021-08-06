from claim.models import ClaimAdmin

from rest_framework import viewsets

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin
from api_fhir_r4.model_retrievers import UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiPractitionerPermissions
from api_fhir_r4.serializers import PractitionerSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class PractitionerViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, viewsets.ModelViewSet):
    retrievers = [UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever]
    serializer_class = PractitionerSerializer
    permission_classes = (FHIRApiPractitionerPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        identifier = request.GET.get("identifier")
        if identifier:
            return self.retrieve(request, *args, **{**kwargs, 'identifier': identifier})
        serializer = PractitionerSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return ClaimAdmin.get_queryset(None, self.request.user)
