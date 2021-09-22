from api_fhir_r4.configurations import GeneralConfiguration, R4ClaimConfig
from claim.models import Claim
from django.utils.translation import gettext as _


class ClaimMapping(object):

    claim_status = {
        f"{Claim.STATUS_REJECTED}": R4ClaimConfig.get_fhir_claim_status_rejected_code(),
        f"{Claim.STATUS_ENTERED}": R4ClaimConfig.get_fhir_claim_status_entered_code(),
        f"{Claim.STATUS_CHECKED}": R4ClaimConfig.get_fhir_claim_status_checked_code(),
        f"{Claim.STATUS_PROCESSED}": R4ClaimConfig.get_fhir_claim_status_processed_code(),
        f"{Claim.STATUS_VALUATED}": R4ClaimConfig.get_fhir_claim_status_valuated_code()
    }

    claim_outcome = {
        f"{Claim.STATUS_REJECTED}": _("complete"),
        f"{Claim.STATUS_ENTERED}": _("queued"),
        f"{Claim.STATUS_CHECKED}": _("partial"),
        f"{Claim.STATUS_PROCESSED}": _("partial"),
        f"{Claim.STATUS_VALUATED}": _("complete")
    }

    visit_type_system = f'{GeneralConfiguration.get_base_url()}CodeSystem/claim-visit-type'
    visit_type = {
        "E": _("Emergency"),
        "R": _("Referrals"),
        "O": _("Other"),
    }
