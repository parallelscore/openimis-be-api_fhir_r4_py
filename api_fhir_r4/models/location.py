from enum import Enum


class LocationMode(Enum):
    INSTANCE = "instance"
    KIND = "kind"


class LocationStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
