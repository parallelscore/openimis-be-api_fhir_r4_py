from rest_framework import viewsets
from insuree.models import Family

from api_fhir_r4.permissions import FHIRApiGroupPermissions
from api_fhir_r4.serializers import GroupSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class GroupViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = GroupSerializer
    permission_classes = (FHIRApiGroupPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        identifier = request.GET.get("identifier")
        if identifier:
            queryset = queryset.filter(head_insuree_id__chf_id=identifier)
        else:
            queryset = queryset.filter(validity_to__isnull=True)
        serializer = GroupSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return Family.objects.all().order_by('validity_from')
