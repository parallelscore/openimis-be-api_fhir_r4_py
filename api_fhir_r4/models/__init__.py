import typing


from api_fhir_r4.exceptions import PropertyTypeError, PropertyError, PropertyMaxSizeError, InvalidAttributeError, \
    UnsupportedFormatError, FHIRException
from django.utils.translation import gettext


SUPPORTED_FORMATS = ['json']


#models from external project fhir resource
from fhir.resources.fhirabstractmodel import FHIRAbstractModel
from fhir.resources.element import Element
from fhir.resources.elementdefinition import ElementDefinition
from fhir.resources.quantity import Quantity
from fhir.resources.resource import Resource
from fhir.resources.address import Address
from fhir.resources.annotation import Annotation
from fhir.resources.attachment import Attachment
from fhir.resources.backboneelement import BackboneElement
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.count import Count
from fhir.resources.distance import Distance
from fhir.resources.domainresource import DomainResource
from fhir.resources.duration import Duration
from fhir.resources.extension import Extension
from fhir.resources.fhirtypes import FHIR_DATE_PARTS
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from api_fhir_r4.models.imisModelEnums import ImisMaritalStatus, ImisClaimIcdTypes, ImisLocationType, ImisHfLevel
from fhir.resources.location import Location, LocationPosition, LocationHoursOfOperation
from fhir.resources.meta import Meta
from fhir.resources.money import Money
from fhir.resources.narrative import Narrative
from fhir.resources.patient import Patient, PatientCommunication, PatientContact, PatientLink
from fhir.resources.group import Group, GroupCharacteristic, GroupMember
from fhir.resources.account import Account
from fhir.resources.organization import Organization, OrganizationContact
from fhir.resources.period import Period
from fhir.resources.range import Range
from fhir.resources.ratio import Ratio
from fhir.resources.reference import Reference
from fhir.resources.sampleddata import SampledData
from fhir.resources.signature import Signature
from fhir.resources.timing import Timing, TimingRepeat
from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue
from fhir.resources.endpoint import Endpoint
from fhir.resources.practitionerrole import PractitionerRole, PractitionerRoleAvailableTime, PractitionerRoleNotAvailable
from fhir.resources.practitioner import Practitioner, PractitionerQualification
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest, BundleEntryResponse, BundleEntrySearch, \
    BundleLink
from fhir.resources.claim import Claim, ClaimAccident, ClaimCareTeam, ClaimDiagnosis, ClaimSupportingInfo, \
    ClaimInsurance, ClaimItem, ClaimItemDetail, ClaimItemDetailSubDetail, ClaimPayee, ClaimProcedure, ClaimRelated
from fhir.resources.coverageeligibilityrequest import CoverageEligibilityRequest, \
    CoverageEligibilityRequestSupportingInfo, CoverageEligibilityRequestInsurance, CoverageEligibilityRequestItem
from fhir.resources.coverageeligibilityresponse import CoverageEligibilityResponse, \
    CoverageEligibilityResponseInsurance, CoverageEligibilityResponseInsuranceItem, \
    CoverageEligibilityResponseInsuranceItemBenefit, CoverageEligibilityResponseError
from fhir.resources.claimresponse import ClaimResponse, ClaimResponseAddItemDetailSubDetail, ClaimResponseError, \
    ClaimResponseItem, ClaimResponseTotal, ClaimResponseAddItem, ClaimResponseAddItemDetail, ClaimResponseInsurance, \
    ClaimResponseItemAdjudication, ClaimResponseItemDetail, ClaimResponseItemDetailSubDetail, ClaimResponsePayment, \
    ClaimResponseProcessNote
from fhir.resources.communicationrequest import CommunicationRequest, CommunicationRequestPayload
from fhir.resources.contract import Contract, ContractFriendly, ContractLegal, ContractRule, ContractSigner, \
    ContractTerm, ContractTermAction, ContractTermAsset, ContractTermOffer, ContractContentDefinition, \
    ContractTermActionSubject, ContractTermAssetContext, ContractTermAssetValuedItem, ContractTermOfferAnswer, \
    ContractTermOfferParty, ContractTermSecurityLabel
from fhir.resources.coverage import Coverage, CoverageClass, CoverageCostToBeneficiary, \
    CoverageCostToBeneficiaryException
from fhir.resources.condition import Condition, ConditionEvidence, ConditionStage
from fhir.resources.medication import MedicationBatch, Medication, MedicationIngredient
from fhir.resources.dosage import Dosage, DosageDoseAndRate
from fhir.resources.expression import Expression
from fhir.resources.usagecontext import UsageContext
from fhir.resources.activitydefinition import ActivityDefinition, ActivityDefinitionDynamicValue, \
    ActivityDefinitionParticipant
from fhir.resources.contactdetail import ContactDetail
from fhir.resources.relatedartifact import RelatedArtifact
from fhir.resources.healthcareservice import HealthcareServiceNotAvailable, HealthcareService, \
    HealthcareServiceAvailableTime, HealthcareServiceEligibility
from fhir.resources.organization import Organization, OrganizationContact


# enumeration types for models value
from api_fhir_r4.models.address import AddressUse, AddressType
from api_fhir_r4.models.activityDefinition import PublicationStatus, RequestResourceType, RequestIntent, RequestPriority
from api_fhir_r4.models.bundle import BundleType, BundleLinkRelation
from api_fhir_r4.models.contactPoint import ContactPointSystem, ContactPointUse
from api_fhir_r4.models.operationOutcome import IssueSeverity
from api_fhir_r4.models.requestStatus import RequestStatus
from api_fhir_r4.models.condition import ConditionClinicalStatusCodes, ConditionVerificationStatus
from api_fhir_r4.models.administrative import AdministrativeGender
from api_fhir_r4.models.daysOfWeek import DaysOfWeek
from api_fhir_r4.models.fhirdate import FHIRDate
from api_fhir_r4.models.humanName import NameUse
from api_fhir_r4.models.identifier import IdentifierUse
from api_fhir_r4.models.imisModelEnums import ImisMaritalStatus, ImisHfLevel, ImisLocationType, ImisClaimIcdTypes
from api_fhir_r4.models.location import LocationMode, LocationStatus
from api_fhir_r4.models.medication import MedicationStatusCodes
from api_fhir_r4.models.relatedArtifact import RelatedArtifactType
from api_fhir_r4.models.usageContext import UsageContextType


# fix of 'issue' type from https://github.com/nazrulworld/fhir.resources/blob/main/fhir/resources/operationoutcome.py#L31
# by overriding 'issue' property. Without this fix - there is no 'issue' field in 'OperationOutcome' model.
from fhir.resources import fhirtypes
from pydantic import Field


class OperationOutcomeV2(OperationOutcome):
    issue: typing.List[fhirtypes.OperationOutcomeIssueType] = Field(
        None,
        alias="issue",
        title="A single issue associated with the action",
        description=(
            "An error, warning, or information message that results from a system "
            "action."
        ),
        # if property is element of this resource.
        element_property=True,
    )


class UsageContextV2(UsageContext):
    code: fhirtypes.CodingType = Field(
        None,
        alias="code",
        title="Type of context being specified",
        description=(
            "A code that identifies the type of context being specified by this "
            "usage context."
        ),
        # if property is element of this resource.
        element_property=True,
    )


class CoverageV2(Coverage):
    payor: typing.List[fhirtypes.ReferenceType] = Field(
        None,
        alias="payor",
        title="Issuer of the policy",
        description=(
            "The program or plan underwriter or payor including both insurance and "
            "non-insurance agreements, such as patient-pay agreements."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Listed Resource Type(s) should be allowed as Reference.
        enum_reference_types=["Organization", "Patient", "RelatedPerson"],
    )


class CoverageClassV2(CoverageClass):
    type: fhirtypes.CodeableConceptType = Field(
        None,
        alias="type",
        title="Type of class such as 'group' or 'plan'",
        description=(
            "The type of classification for which an insurer-specific class label "
            "or number and optional name is provided, for example may be used to "
            "identify a class of coverage or employer group, Policy, Plan."
        ),
        # if property is element of this resource.
        element_property=True,
    )


from api_fhir_r4.models import OperationOutcomeV2
from api_fhir_r4.models import UsageContextV2
from api_fhir_r4.models import CoverageV2
from api_fhir_r4.models import CoverageClassV2
