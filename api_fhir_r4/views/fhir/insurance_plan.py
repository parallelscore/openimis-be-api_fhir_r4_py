from rest_framework import viewsets
from product.models import Product

from api_fhir_r4.mixins import MultiIdentifierRetrieverMixin, MultiIdentifierUpdateMixin
from api_fhir_r4.model_retrievers import UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever
from api_fhir_r4.permissions import FHIRApiProductPermissions
from api_fhir_r4.serializers import InsurancePlanSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class ProductViewSet(BaseFHIRView, MultiIdentifierRetrieverMixin, MultiIdentifierUpdateMixin, viewsets.ModelViewSet):
    retrievers = [UUIDIdentifierModelRetriever, CodeIdentifierModelRetriever]
    serializer_class = InsurancePlanSerializer
    permission_classes = (FHIRApiProductPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        identifier = request.GET.get("identifier")
        if identifier:
            return self.retrieve(request, *args, **{**kwargs, 'identifier': identifier})
        else:
            queryset = queryset.filter(validity_to__isnull=True)
        serializer = InsurancePlanSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, *args, **kwargs):
        response = super().retrieve(self, *args, **kwargs)
        return response

    def get_queryset(self):
        return Product.objects.all().order_by('validity_from')