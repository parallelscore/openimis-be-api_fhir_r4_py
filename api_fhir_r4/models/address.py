from enum import Enum


class AddressUse(Enum):
    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    BILLING = 'billing'


class AddressType(Enum):
    POSTAL = "postal"
    PHYSICAL = "physical"
    BOTH = "both"
