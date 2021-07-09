from enum import Enum


class PublicationStatus(Enum):

    DRAFT = 'draft'
    ACTIVE = 'active'
    RETIRED = 'retired'
    UNKNOWN = 'unknown'


class RequestResourceType(Enum):

    APPOINTMENT = 'appointment'
    APPOINTMENT_RESPONSE = 'appointmentResponse'
    CARE_PLAN = 'carePlan'
    CLAIM = 'claim'
    COMMUNICATION_REQUEST = 'communicationRequest'
    CONTRACT = 'contract'
    DEVICE_REQUEST = 'deviceRequest'
    ENROLLMENT_REQUEST = 'enrollmentRequest'
    IMMUNIZATION_RECOMMENDATION = 'immunizationRecommendation'
    MEDICATION_REQUEST = 'medicationRequest'
    NUTRITION_ORDER = 'nutritionOrder'
    SERVICE_REQUEST = 'serviceRequest'
    SUPPLY_REQUEST = 'supplyRequest'
    TASK = 'task'
    VISION_PRESCRIPTION = 'visionPrescription'


class RequestIntent(Enum):

    PROPOSAL = 'proposal'
    PLAN = 'plan'
    DIRECTIVE = 'directive'
    ORDER = 'order'
    ORIGINAL_ORDER = 'original-order'
    REFLEX_ORDER = 'reflex-order'
    FILLER_ORDER = 'filler-order'
    INSTANCE_ORDER = 'instance-order'
    OPTION = 'option'


class RequestPriority(Enum):

    ROUTINE = 'routine'
    URGENT = 'urgent'
    ASAP = 'asap'
    STAT = 'stat'
