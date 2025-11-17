def to_myanmar_date(ymd):
    """
    Convert 2025-01-09 → ၂၀၂၅ ခုနှစ်၊ ဇန်နဝါရီလ ၉ ရက်
    """
    import calendar

    # 1) English → Myanmar digits
    my_digits = str.maketrans("0123456789", "၀၁၂၃၄၅၆၇၈၉")

    year = ymd.year
    month = ymd.month
    day = ymd.day

    # 2) Month names dictionary
    myanmar_months = [
        "", "ဂျန်နဝါရီ", "ဖေဖော်ဝါရီ", "မတ်ချ်",
        "ဧပြီ", "မေ", "ဂျုန်",
        "ဂျူလိုင်", "သြဂတ်စ်", "စပ်တမ်ဘာ",
        "အောက်တိုဘာ", "နိုဗမ်ဘာ", "ဒီဇင်ဘာ"
    ]

    # 3) Format Myanmar style
    formatted = f"{year} ခုနှစ်၊ {myanmar_months[month]}လ ({day}) ရက်"

    # 4) Digits to Myanmar digits
    return formatted.translate(my_digits)

def to_myanmar_date_formatted(ymd):
    """
    Convert 2025-01-09 → ၂၀၂၅ ခုနှစ်၊ ဇန်နဝါရီလ ၉ ရက်
    """
    import calendar

    # 1) English → Myanmar digits
    my_digits = str.maketrans("0123456789", "၀၁၂၃၄၅၆၇၈၉")

    year = ymd.year
    month = ymd.month
    day = ymd.day

    # 2) Month names dictionary
    myanmar_months = [
        "", "ဂျန်နဝါရီ", "ဖေဖော်ဝါရီ", "မတ်ချ်",
        "ဧပြီ", "မေ", "ဂျုန်",
        "ဂျူလိုင်", "သြဂတ်စ်", "စပ်တမ်ဘာ",
        "အောက်တိုဘာ", "နိုဗမ်ဘာ", "ဒီဇင်ဘာ"
    ]

    # 3) Format Myanmar style
    formatted_date= f"{year} ခုနှစ်၊ {myanmar_months[month]}လ {day} ရက်"

    # 4) Digits to Myanmar digits
    return formatted_date.translate(my_digits)
