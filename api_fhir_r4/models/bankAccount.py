from api_fhir_r4.models import Element, Property

class BankAccount(Element):
    bank = Property('bank', str)  # NameUse
    no = Property('no', str)