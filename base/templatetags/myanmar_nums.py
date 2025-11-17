# het/templatetags/myanmar_nums.py
from django import template

register = template.Library()

# English → Myanmar number mapping
EN = "0123456789"
MM = "၀၁၂၃၄၅၆၇၈၉"
TRANS = str.maketrans(EN, MM)
MONTHS = [
    "ဇန်နဝါရီလ", 
    "ဖေဖော်ဝါရီလ",
    "မတ်လ",
    "ဧပြီလ",
    "မေလ",
    "ဇွန်လ",
    "ဇူလိုင်လ",
    "ဩဂုတ်လ",
    "စက်တင်ဘာလ",
    "အောက်တိုဘာလ",
    "နိုဝင်ဘာလ",
    "ဒီဇင်ဘာလ",
]

@register.filter
def mymonth(value):
    """
    Convert month number (1–12) to Myanmar month name.
    Usage: {{ month|mymonth }}
    """
    if not value:
        return ""

    try:
        index = int(value) - 1
        return MONTHS[index]
    except (ValueError, IndexError):
        return str(value)
@register.filter
def mynum(value):
    """
    Convert English digits to Myanmar digits.
    Usage: {{ number|mynum }}
    """
    if value is None:
        return ""
    return str(value).translate(TRANS)
