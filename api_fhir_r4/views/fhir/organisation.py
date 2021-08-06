from rest_framework import viewsets

from policyholder.models import PolicyHolder

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin
from api_fhir_r4.model_retrievers import CodeIdentifierModelRetriever, DatabaseIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiOrganizationPermissions
from api_fhir_r4.serializers import OrganisationSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class OrganisationViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, viewsets.ModelViewSet):
    retrievers = [DatabaseIdentifierModelRetriever, CodeIdentifierModelRetriever]
    serializer_class = OrganisationSerializer
    permission_classes = (FHIRApiOrganizationPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        identifier = request.GET.get("code")
        if identifier:
            return self.retrieve(request, *args, **{**kwargs, 'identifier': identifier})
        else:
            queryset = queryset.filter().order_by('date_created')
        serializer = OrganisationSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return PolicyHolder.objects.filter(is_deleted=False).order_by('date_created')
