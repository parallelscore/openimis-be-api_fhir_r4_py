from enum import Enum


class ConditionClinicalStatusCodes(Enum):

    ACTIVE = 'active'
    RECURRENCE = 'recurrence'
    RELAPSE = 'relapse'
    INACTIVE = 'inactive'
    REMISSION = 'remission'
    RESOLVED = 'resolved'


class ConditionVerificationStatus(Enum):

    UNCONFIRMED = 'unconfirmed'
    PROVISIONAL = 'provisional'
    DIFFERENTIAL = 'differential'
    CONFIRMED = 'confirmed'
    REFUTED = 'refuted'
    ENTERED_IN_ERROR = 'entered-in-error'
