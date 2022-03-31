from typing import Union

from api_fhir_r4.models import Subscription
from core.datetimes.ad_datetime import datetime
from core.models import HistoryModel, VersionedModel


class SubscriptionCriteriaFilter:
    def __init__(self, imis_resource: Union[HistoryModel, VersionedModel], fhir_resource_type: str):
        self.resource_type = fhir_resource_type
        self.imis_resource = imis_resource

    def get_filtered_subscriptions(self):
        subscriptions = self._get_all_active_subscriptions()
        return self._get_matching_subscriptions(subscriptions)

    def _get_all_active_subscriptions(self):
        return Subscription.objects.filter(
            criteria__jsoncontains={'resource_type': self.resource_type},
            status=Subscription.SubscriptionStatus.ACTIVE.value,
            expiring__gt=datetime.now(),
            is_deleted=False).all()

    def _get_matching_subscriptions(self, subscriptions):
        return [subscription for subscription in subscriptions
                if self._is_matching_subscription(subscription)]

    def _is_matching_subscription(self, sub):
        criteria = {criteria: sub.criteria[criteria] for criteria in sub.criteria if criteria != 'resource_type'}
        return not criteria or self._is_resource_matching_criteria(criteria)

    def _is_resource_matching_criteria(self, criteria):
        criteria['uuid'] = self.imis_resource.uuid
        return type(self.imis_resource).objects.filter(**criteria).exists()
