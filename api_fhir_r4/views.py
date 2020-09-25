from api_fhir_r4.converters import OperationOutcomeConverter
from api_fhir_r4.permissions import FHIRApiClaimPermissions, FHIRApiCoverageEligibilityRequestPermissions, \
    FHIRApiCoverageRequestPermissions, FHIRApiCommunicationRequestPermissions, FHIRApiPractitionerPermissions, \
    FHIRApiHFPermissions, FHIRApiInsureePermissions, FHIRApiMedicationPermissions, FHIRApiConditionPermissions, \
    FHIRApiActivityDefinitionPermissions, FHIRApiHealthServicePermissions
from claim.models import ClaimAdmin, Claim, Feedback
from django.db.models import OuterRef, Exists
from insuree.models import Insuree
from location.models import HealthFacility, Location
from policy.models import Policy
from medical.models import Item, Diagnosis, Service
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
import datetime
from api_fhir_r4.paginations import FhirBundleResultsSetPagination
from api_fhir_r4.permissions import FHIRApiPermissions
from api_fhir_r4.configurations import R4CoverageEligibilityConfiguration as Config
from api_fhir_r4.serializers import PatientSerializer, LocationSerializer, LocationSiteSerializer, PractitionerRoleSerializer, \
    PractitionerSerializer, ClaimSerializer, CoverageEligibilityRequestSerializer, \
    PolicyCoverageEligibilityRequestSerializer, ClaimResponseSerializer, CommunicationRequestSerializer, \
    MedicationSerializer, ConditionSerializer, ActivityDefinitionSerializer, HealthcareServiceSerializer
from api_fhir_r4.serializers.coverageSerializer import CoverageSerializer
from django.db.models import Q
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class BaseFHIRView(APIView):
    pagination_class = FhirBundleResultsSetPagination
    permission_classes = (FHIRApiPermissions,)
    authentication_classes = [CsrfExemptSessionAuthentication] + APIView.settings.DEFAULT_AUTHENTICATION_CLASSES


class InsureeViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = PatientSerializer
    #permission_classes = (FHIRApiInsureePermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() 
        queryset.select_related('Family__Photo__Gender')
        refDate = request.GET.get('refDate')
        claim_date = request.GET.get('claimDateFrom')
        identifier = request.GET.get("identifier")
        if identifier:
            queryset = queryset.filter(chf_id=identifier)
        else:
            queryset = queryset.filter(validity_to__isnull=True).order_by('chf_id')
            if refDate != None:
                year,month,day = refDate.split('-')
                isValidDate = True
                try :
                    datetime.datetime(int(year),int(month),int(day))
                except ValueError :
                    isValidDate = False
                datevar = refDate
                queryset = queryset.filter(validity_from__gte=datevar)
            if claim_date is not None:
                year,month,day = refDate.split('-')
                try:
                    claim_date_parsed = datetime.datetime(int(year), int(month), int(day))
                except ValueError:
                    result = OperationOutcomeConverter.build_for_400_bad_request("claimDateFrom should be in dd-mm-yyyy format")
                    return Response(result.toDict(), status.HTTP_400_BAD_REQUEST)
                has_claim_in_range = Claim.objects\
                    .filter(date_claimed__gte=claim_date_parsed)\
                    .filter(insuree_id=OuterRef("id"))\
                    .values("id")
                queryset = queryset.annotate(has_claim_in_range=Exists(has_claim_in_range)).filter(has_claim_in_range=True)
            
        
        serializer = PatientSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    
    def get_queryset(self):
        return Insuree.objects.all()
        
 
        
class LocationViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = LocationSerializer
    #permission_classes = (FHIRApiHFPermissions,)

    def list(self, request, *args, **kwargs):
        identifier = request.GET.get("identifier")
        physicalType = request.GET.get('physicalType')
        queryset = self.get_queryset(physicalType)
        if identifier:
            queryset = queryset.filter(code=identifier)
        else:
            queryset = queryset.filter(validity_to__isnull=True)
        if ( physicalType and physicalType == 'si'):
            self.serializer_class=LocationSiteSerializer
            serializer = LocationSiteSerializer(self.paginate_queryset(queryset), many=True)
        else:
            serializer = LocationSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, *args, **kwargs):
        physicalType = self.request.GET.get('physicalType')
        if ( physicalType and physicalType == 'si'):
            self.serializer_class=LocationSiteSerializer
            self.queryset = self.get_queryset('si')
        response = viewsets.ModelViewSet.retrieve(self, *args, **kwargs)
        return response

    def get_queryset(self, physicalType = 'area'):
        #return Location.get_queryset(None, self.request.user)
        if physicalType == 'si':
            return HealthFacility.objects.all()
        else:
            return Location.objects.all()
        
class PractitionerRoleViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = PractitionerRoleSerializer
    #permission_classes = (FHIRApiPractitionerPermissions,)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if identifier:
            queryset = queryset.filter(code=identifier)
    def perform_destroy(self, instance):
        instance.health_facility_id = None
        instance.save()

    def get_queryset(self):
        #return ClaimAdmin.get_queryset(None, self.request.user)
        return ClaimAdmin.objects.all()


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
        #return ClaimAdmin.get_queryset(None, self.request.user)
        return ClaimAdmin.filter_queryset(None)

class ClaimViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                   mixins.CreateModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = ClaimSerializer
    #permission_classes = (FHIRApiClaimPermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        refDate = request.GET.get('refDate')
        identifier = request.GET.get("identifier")
        patient = request.GET.get("patient")
        if identifier is not None:
            queryset = queryset.filter(identifier=identifier)
        else:
            queryset = queryset.filter(validity_to__isnull=True)
            if refDate is not None:
                year,month,day = refDate.split('-')
                isValidDate = True
                try :
                    datetime.datetime(int(year),int(month),int(day))
                except ValueError :
                    isValidDate = False
                datevar = refDate
                queryset = queryset.filter(validity_from__gte=datevar)
            if patient is not None:
                for_patient = Insuree.objects\
                    .filter(indentifier = patient)\
                    .values("id")
                queryset = queryset.filter(chf_id in indentifier.id)
        serializer = ClaimSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        #return Claim.get_queryset(None, self.request.user)
        return Claim.objects.all()


class ClaimResponseViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = ClaimResponseSerializer
    permission_classes = (FHIRApiClaimPermissions,)

    def get_queryset(self):
        return Claim.get_queryset(None, self.request.user)


class CommunicationRequestViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = CommunicationRequestSerializer
    permission_classes = (FHIRApiCommunicationRequestPermissions,)

    def get_queryset(self):
        return Feedback.get_queryset(None, self.request.user)


class CoverageEligibilityRequestViewSet(BaseFHIRView, mixins.CreateModelMixin, GenericViewSet):
    queryset = Insuree.filter_queryset()
    serializer_class = eval(Config.get_serializer())
    #serializer_class = CoverageEligibilityRequestSerializer
    permission_classes = (FHIRApiCoverageEligibilityRequestPermissions,)

    def get_queryset(self):
        return Insuree.get_queryset(None, self.request.user)


class CoverageRequestQuerySet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = CoverageSerializer
    permission_classes = (FHIRApiCoverageRequestPermissions,)

    def get_queryset(self):
        return Policy.get_queryset(None, self.request.user)


class MedicationViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = MedicationSerializer
    permission_classes = (FHIRApiMedicationPermissions,)

    def get_queryset(self):
        return Item.get_queryset(None, self.request.user)


class ConditionViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'id'
    serializer_class = ConditionSerializer
    permission_classes = (FHIRApiConditionPermissions,)

    def get_queryset(self):
        return Diagnosis.get_queryset(None, self.request.user)


class ActivityDefinitionViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = ActivityDefinitionSerializer
    permission_classes = (FHIRApiActivityDefinitionPermissions,)

    def get_queryset(self):
        return Service.get_queryset(None, self.request.user)


class HealthcareServiceViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = HealthcareServiceSerializer
    #permission_classes = (FHIRApiHealthServicePermissions,)

    def get_queryset(self):
        #return HealthFacility.get_queryset(None, self.request.user)
        return HealthFacility.get_queryset(None, self.request.user)
