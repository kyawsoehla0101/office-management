# het/templatetags/myanmar_nums.py
from django import template

register = template.Library()

# English → Myanmar number mapping
EN = "0123456789"
MM = "၀၁၂၃၄၅၆၇၈၉"
TRANS = str.maketrans(EN, MM)

@register.filter
def mynum(value):
    """
    Convert English digits to Myanmar digits.
    Usage: {{ number|mynum }}
    """
    if value is None:
        return ""
    return str(value).translate(TRANS)
