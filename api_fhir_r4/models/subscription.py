from django.db import models
from django.utils.translation import gettext as _
from django_cryptography.fields import encrypt
from jsonfallback.fields import FallbackJSONField

from core.models import HistoryBusinessModel


class Subscription(HistoryBusinessModel):
    class SubscriptionStatus(models.IntegerChoices):
        INACTIVE = 0, _('inactive')
        ACTIVE = 1, _('active')

    class SubscriptionChannel(models.IntegerChoices):
        REST_HOOK = 0, _("rest-hook")

    status = models.SmallIntegerField(db_column='Status', null=False, choices=SubscriptionStatus.choices)
    channel = models.SmallIntegerField(db_column='Channel', null=False, choices=SubscriptionChannel.choices)
    endpoint = models.CharField(db_column='Endpoint', max_length=255, null=False)
    headers = encrypt(models.TextField(db_column='Headers', null=True))
    criteria = FallbackJSONField(db_column='Criteria', null=True)
    expiring = models.DateTimeField(db_column='Expiring', null=False)

    class Meta:
        managed = True
        db_table = 'tblSubscription'
