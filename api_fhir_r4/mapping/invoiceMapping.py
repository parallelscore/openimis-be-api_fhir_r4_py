from django.utils.translation import gettext as _


class ChargeItemMapping(object):

    charge_item = {
        "policy": {
            "code": "policy",
            "display": _("Policy"),
        },
        "contractcontributionplandetails": {
            "code": "contribution",
            "display": _("Contribution")
        },
    }
