from claim.models import ClaimAdmin

from rest_framework import viewsets

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin
from api_fhir_r4.model_retrievers import CodeIdentifierModelRetriever, UUIDIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiPractitionerPermissions
from api_fhir_r4.serializers import PractitionerRoleSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class PractitionerRoleViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, viewsets.ModelViewSet):
    retrievers = [UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever]
    serializer_class = PractitionerRoleSerializer
    permission_classes = (FHIRApiPractitionerPermissions,)

    def list(self, request, *args, **kwargs):
        identifier = request.GET.get("identifier")
        queryset = self.get_queryset()
        if identifier:
            return self.retrieve(request, *args, **{**kwargs, 'identifier': identifier})
        else:
            queryset = queryset.filter(validity_to__isnull=True).order_by('validity_from')

        serializer = PractitionerRoleSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def perform_destroy(self, instance):
        instance.health_facility_id = None
        instance.save()

    def get_queryset(self):
        return ClaimAdmin.get_queryset(None, self.request.user)
