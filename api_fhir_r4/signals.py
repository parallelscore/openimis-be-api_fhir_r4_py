import logging

from django.core.exceptions import ObjectDoesNotExist

from api_fhir_r4.converters import PatientConverter, GroupConverter, ClaimAdminPractitionerConverter, BillInvoiceConverter, CoverageConverter, ClaimConverter, InvoiceConverter, \
    HealthFacilityOrganisationConverter, MedicationConverter, ActivityDefinitionConverter
from api_fhir_r4.mapping.invoiceMapping import InvoiceTypeMapping, BillTypeMapping
from api_fhir_r4.subscriptions.notificationManager import RestSubscriptionNotificationManager
from api_fhir_r4.subscriptions.subscriptionCriteriaFilter import SubscriptionCriteriaFilter
from core.service_signals import ServiceSignalBindType
from core.signals import bind_service_signal

from openIMIS.openimisapps import openimis_apps

logger = logging.getLogger('openIMIS')
imis_modules = openimis_apps()


def bind_service_signals():
    if 'insuree' in imis_modules:
        def on_insuree_create_or_update(**kwargs):
            model = kwargs.get('result', None)
            if model:
                notify_subscribers(model, PatientConverter(), 'Patient', None)

        bind_service_signal(
            'insuree_service.create_or_update',
            on_insuree_create_or_update,
            bind_type=ServiceSignalBindType.AFTER
        )

        def on_family_create_or_update(**kwargs):
            model = kwargs.get('result', None)
            if model:
                notify_subscribers(model, GroupConverter(), 'Group', None)

        bind_service_signal(
            'family_service.create_or_update',
            on_family_create_or_update,
            bind_type=ServiceSignalBindType.AFTER
        )

    if 'location' in imis_modules:
        def on_hf_create_or_update(**kwargs):
            model = kwargs.get('result', None)
            if model:
                notify_subscribers(
                    model, HealthFacilityOrganisationConverter(), 'Organization', 'bus')

        bind_service_signal(
            'health_facility_service.update_or_create',
            on_hf_create_or_update,
            bind_type=ServiceSignalBindType.AFTER
        )

    if 'invoice' in imis_modules:
        from invoice.models import Bill, Invoice

        def on_bill_create(**kwargs):
            result = kwargs.get('result', {})
            if result and result.get('success', False):
                model_uuid = result['data']['uuid']
                try:
                    model = Bill.objects.get(uuid=model_uuid)
                    notify_subscribers(model, BillInvoiceConverter(), 'Invoice',
                                       BillTypeMapping.invoice_type[model.subject_type.model])
                except ObjectDoesNotExist:
                    logger.error(
                        f'Bill returned from service does not exists ({model_uuid})')
                    import traceback
                    logger.debug(traceback.format_exc())

        def on_invoice_create(**kwargs):
            result = kwargs.get('result', {})
            if result and result.get('success', False):
                model_uuid = result['data']['uuid']
                try:
                    model = Invoice.objects.get(uuid=model_uuid)
                    notify_subscribers(model, InvoiceConverter(), 'Invoice',
                                       InvoiceTypeMapping.invoice_type[model.subject_type.model])
                except ObjectDoesNotExist:
                    logger.error(
                        f'Invoice returned from service does not exists ({model_uuid})')
                    import traceback
                    logger.debug(traceback.format_exc())

        bind_service_signal(
            'signal_after_invoice_module_bill_create_service',
            on_bill_create,
            bind_type=ServiceSignalBindType.AFTER
        )
        bind_service_signal(
            'signal_after_invoice_module_invoice_create_service',
            on_invoice_create,
            bind_type=ServiceSignalBindType.AFTER
        )

    if 'policy' in imis_modules:
        def on_policy_create_or_update(**kwargs):
            model = kwargs.get('result', None)
            if model:
                notify_subscribers(
                    model, CoverageConverter(), 'Coverage', None)

        bind_service_signal(
            'policy_service.create_or_update',
            on_policy_create_or_update,

            bind_type=ServiceSignalBindType.AFTER
        )

    if 'claim' in imis_modules:
        # claim.enter_and_submit_claim
        def on_claim_enter_or_submit(**kwargs):

            model = kwargs.get('result', None)

            if model:
                notify_subscribers(
                    model, ClaimConverter(), 'Claim', None)

        bind_service_signal(
            'claim.enter_and_submit_claim',
            on_claim_enter_or_submit,

            bind_type=ServiceSignalBindType.AFTER
        )

        def on_claimadmin_created_or_updated(**kwargs):

            model = kwargs.get('result', None)

            if model:
                notify_subscribers(
                    model, ClaimAdminPractitionerConverter(), 'Practitioner', None)

        bind_service_signal(
            'claimadmin.create_or_update',
            on_claimadmin_created_or_updated,

            bind_type=ServiceSignalBindType.AFTER
        )

    if 'medical' in imis_modules:
        def on_medication_item_create_or_update(**kwargs):
            model = kwargs.get('result', None)
            if model:
                notify_subscribers(
                    model, MedicationConverter(), 'Medication', None)

        def on_medication_service_create_or_update(**kwargs):
            model = kwargs.get('result', None)
            if model:
                notify_subscribers(
                    model, ActivityDefinitionConverter(), 'ActivityDefinition', None)

        bind_service_signal(
            'medication_item.create_or_update',
            on_medication_item_create_or_update,

            bind_type=ServiceSignalBindType.AFTER
        )

        bind_service_signal(
            'medication_service.create_or_update',
            on_medication_service_create_or_update,

            bind_type=ServiceSignalBindType.AFTER
        )


def notify_subscribers(model, converter, resource_name, resource_type_name):
    try:
        subscriptions = SubscriptionCriteriaFilter(model, resource_name,
                                                   resource_type_name).get_filtered_subscriptions()
        RestSubscriptionNotificationManager(
            converter).notify_subscribers_with_resource(model, subscriptions)
    except Exception as e:
        logger.error(f'Notifying subscribers failed: {e}')
        import traceback
        logger.debug(traceback.format_exc())
