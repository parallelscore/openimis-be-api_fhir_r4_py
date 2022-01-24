from api_fhir_r4.models import Subscription
from core.services import BaseService
from core.validation import BaseModelValidation


class SubscriptionService(BaseService):
    OBJECT_TYPE = Subscription

    def __init__(self, user, validation_class=BaseModelValidation):
        super().__init__(user, validation_class)
