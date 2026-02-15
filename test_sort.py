from base.utils.sort_utils import sort_members_custom
from collections import namedtuple

# Mock Member class
Member = namedtuple("Member", ["reg_no"])

# Test cases
test_data = [
    Member(reg_no="123"),
    Member(reg_no="AC-123"),
    Member(reg_no="AC-10"),
    Member(reg_no="AC-100"),
    Member(reg_no="5"),
    Member(reg_no="AA-999"),
    Member(reg_no=None),
]

sorted_data = sort_members_custom(test_data)

print("Original:")
for m in test_data:
    print(f"  {m.reg_no}")

print("\nSorted:")
for m in sorted_data:
    print(f"  {m.reg_no}")
