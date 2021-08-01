from location.models import HealthFacility, Location
from rest_framework import viewsets

from api_fhir_r4.permissions import FHIRApiHFPermissions
from api_fhir_r4.serializers import LocationSerializer, LocationSiteSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class LocationViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = LocationSerializer
    permission_classes = (FHIRApiHFPermissions,)

    def list(self, request, *args, **kwargs):
        identifier = request.GET.get("identifier")
        physical_type = request.GET.get('physicalType')
        queryset = self.get_queryset(physical_type)
        if identifier:
            queryset = queryset.filter(code=identifier)
        else:
            queryset = queryset.filter(validity_to__isnull=True).order_by('validity_from')
        if physical_type and physical_type == 'si':
            self.serializer_class=LocationSiteSerializer
            serializer = LocationSiteSerializer(self.paginate_queryset(queryset), many=True)
        else:
            serializer = LocationSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, *args, **kwargs):
        physical_type = self.request.GET.get('physicalType')
        if physical_type and physical_type == 'si':
            self.serializer_class=LocationSiteSerializer
            self.queryset = self.get_queryset('si')
        response = viewsets.ModelViewSet.retrieve(self, *args, **kwargs)
        return response

    def get_queryset(self, physicalType='area'):
        if physicalType == 'si':
            hf_queryset = HealthFacility.get_queryset(None, self.request.user)
            return hf_queryset.select_related('location').select_related('sub_level').select_related('legal_form')
        else:
            return Location.get_queryset(None, self.request.user)
