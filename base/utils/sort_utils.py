import re

def sort_members_custom(members):
    """
    Sorts members list:
    1. Members with 'AC' in reg_no come first.
    2. Then sorted by Rank (Higher rank first).
    3. Then sorted by the numeric part of reg_no in ascending order.
    """
    
    # Rank weights (Higher number = Higher rank)
    RANK_WEIGHTS = {
        'general': 12,
        'colonel': 11,
        'major': 10,
        'captain': 9,
        'lieutenant': 8,
        'second Lieutenant': 7,
        'warrant_officer_class-1': 6,
        'warrant_officer_class-2': 5,
        'sergeant': 4,
        'coporal': 3,
        'lance_corporal': 2,
        'private': 1,
    }

    def sort_key(member):
        reg_no = str(member.reg_no) if member.reg_no else ""
        rank = member.rank if member.rank else ""
        
        # Check for AC (case insensitive)
        has_ac = "AC" in reg_no.upper()
        
        # Get Rank Weight
        rank_weight = RANK_WEIGHTS.get(rank, 0)

        # Convert Myanmar digits to English digits for sorting purposes
        mm_to_en = str.maketrans("၀၁၂၃၄၅၆၇၈၉", "0123456789")
        reg_no_en = reg_no.translate(mm_to_en)
        
        # Extract first numeric sequence
        numbers = re.findall(r'\d+', reg_no_en)
        # If no number, treat as infinity so it goes to the end
        number = int(numbers[0]) if numbers else float('inf')
        
        # Tuple comparison:
        # 1. not has_ac: False (0) comes before True (1). So AC first.
        # 2. -rank_weight: Higher weight (more negative) comes first.
        # 3. number: Lower comes first.
        # 4. reg_no: Tie breaker.
        return (not has_ac, -rank_weight, number, reg_no)

    # Convert to list and sort
    members_list = list(members)
    members_list.sort(key=sort_key)
    return members_list
