from rest_framework import viewsets
from insuree.models import Family

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin
from api_fhir_r4.model_retrievers import UUIDIdentifierModelRetriever, GroupIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiGroupPermissions
from api_fhir_r4.serializers import GroupSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class GroupViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, viewsets.ModelViewSet):
    retrievers = [UUIDIdentifierModelRetriever, GroupIdentifierModelRetriever]
    serializer_class = GroupSerializer
    permission_classes = (FHIRApiGroupPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        identifier = request.GET.get("identifier")
        if identifier:
            return self.retrieve(request, *args, **{**kwargs, 'identifier': identifier})
        else:
            queryset = queryset.filter(validity_to__isnull=True)
        serializer = GroupSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return Family.objects.all().order_by('validity_from')
