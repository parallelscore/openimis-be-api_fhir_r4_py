from enum import Enum


class IssueSeverity(Enum):
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"
