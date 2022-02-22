from typing import Type

from django.core.exceptions import ValidationError

from api_fhir_r4.models import Subscription
from core.models import HistoryModel
from core.validation import BaseModelValidation


class SubscriptionValidation(BaseModelValidation):
    OBJECT_TYPE = Subscription

    allowed_resources = ('patient', 'invoice')

    @classmethod
    def validate_create(cls, user, **data):
        cls.check_allowed_resources(**data)

    @classmethod
    def validate_update(cls, user, **data):
        cls.check_allowed_resources(**data)

    @classmethod
    def validate_delete(cls, user, **data):
        super().validate_delete(user, **data)

    @classmethod
    def check_allowed_resources(cls, **data):
        resource_type = data.get('criteria', {}).get('resource_type', '').lower()
        if not resource_type or resource_type not in cls.allowed_resources:
            raise ValidationError(f'Resource type not allowed: {resource_type}')
