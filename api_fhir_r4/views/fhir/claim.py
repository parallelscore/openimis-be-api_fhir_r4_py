import datetime

from django.db.models import Prefetch, Q

from insuree.models import Insuree, InsureePolicy
from claim.models import Claim, Feedback, ClaimItem, ClaimService
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.permissions import FHIRApiClaimPermissions
from api_fhir_r4.serializers import ClaimSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class ClaimViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                   mixins.CreateModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = ClaimSerializer
    permission_classes = (FHIRApiClaimPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()\
            .select_related('insuree').select_related('health_facility').select_related('icd')\
            .select_related('icd_1').select_related('icd_2').select_related('icd_3').select_related('icd_4')\
            .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True)))\
            .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True)))\
            .prefetch_related(Prefetch(
                'insuree__insuree_policies',
                queryset=InsureePolicy.objects.filter(validity_to__isnull=True).select_related("policy")
            ))

        refDate = request.GET.get('refDate')
        identifier = request.GET.get("identifier")
        patient = request.GET.get("patient")
        contained = bool(request.GET.get("contained"))

        if identifier is not None:
            queryset = queryset.filter(Q(code=identifier) | Q(id=identifier) | Q(uuid=identifier))
        else:
            queryset = queryset.filter(validity_to__isnull=True).order_by('validity_from')
            if refDate is not None:
                year, month, day = refDate.split('-')
                try:
                    datetime.datetime(int(year), int(month), int(day))
                except ValueError:
                    pass

                datevar = refDate
                queryset = queryset.filter(validity_from__gte=datevar)
            if patient is not None:
                for_patient = Insuree.objects\
                    .filter(indentifier=patient)\
                    .values("id")
                queryset = queryset.filter(chf_id in indentifier.id)
        serializer = ClaimSerializer(self.paginate_queryset(queryset), many=True, context={'contained': contained},
                                     reference_type='db_id_reference')
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        contained = bool(request.GET.get("contained"))
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'contained': contained})
        return Response(serializer.data)

    def get_queryset(self):
        return Claim.get_queryset(None, self.request.user)
