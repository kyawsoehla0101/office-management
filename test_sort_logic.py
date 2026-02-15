
import re
from collections import namedtuple

# Mock Member class
Member = namedtuple("Member", ["reg_no", "full_name"])

def sort_members_custom(members):
    """
    Sorts members list:
    1. Members with 'AC' in reg_no come first.
    2. Then sorted by the numeric part of reg_no in ascending order.
    """
    def sort_key(member):
        reg_no = str(member.reg_no) if member.reg_no else ""
        
        # Check for AC (case insensitive)
        has_ac = "AC" in reg_no.upper()
        
        # Extract first numeric sequence
        numbers = re.findall(r'\d+', reg_no)
        # If no number, treat as infinity so it goes to the end (or 0 if preferred?)
        number = int(numbers[0]) if numbers else float('inf')
        
        # Tuple comparison:
        # 1. not has_ac: False (0) comes before True (1). So AC first.
        # 2. number: Lower comes first.
        # 3. reg_no: Tie breaker.
        return (not has_ac, number, reg_no)

    # Convert to list and sort
    members_list = list(members)
    members_list.sort(key=sort_key)
    return members_list

# Test Data
members = [
    Member("123", "User 123"),
    Member("5", "User 5"),
    Member("AC-100", "AC 100"),
    Member("AC-10", "AC 10"),
    Member("AC-2", "AC 2"),
    Member("B-50", "B 50"),
    Member(None, "None Reg"),
    Member("", "Empty Reg"),
]

sorted_members = sort_members_custom(members)

print("Original:")
for m in members:
    print(f"{m.reg_no}: {m.full_name}")

print("\nSorted:")
for m in sorted_members:
    print(f"{m.reg_no}: {m.full_name}")
