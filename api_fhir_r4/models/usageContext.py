from enum import Enum


class UsageContextType(Enum):

    GENDER = 'gender'
    AGE_RANGE = 'age'
    CLINICAL_FOCUS = 'focus'
    USER_TYPE = 'user'
    WORKFLOW_SETTING = 'workflow'
    WORKFLOW_TASK = 'task'
    CLINICAL_VENUE = 'venue'
    SPECIES = 'species'
    PROGRAM = 'program'
