from enum import Enum


class MedicationStatusCodes(Enum):

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ENTERED_IN_ERROR = 'entered-in-error'
