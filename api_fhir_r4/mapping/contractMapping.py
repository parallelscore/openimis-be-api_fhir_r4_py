from django.utils.translation import gettext as _


class PayTypeMapping(object):

    pay_type = {
        "B": _("Bank transfer"),
        "C": _("Cash"),
        "M": _("Mobile phone"),
        "F": _("Funding")
    }
