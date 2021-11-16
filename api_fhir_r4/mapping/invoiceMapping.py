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


class InvoiceTypeMapping(object):

    invoice_type = {
        "family": {
            "code": "contribution",
            "display": _("Contribution"),
        },
        "contract": {
            "code": "contract",
            "display": _("Contract")
        },
    }
