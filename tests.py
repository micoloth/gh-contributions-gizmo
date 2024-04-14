

from datetime import date
from main import get_week_number

# # % [
assert get_week_number(date(2024, 1, 1)) == 0
assert get_week_number(date(2024, 1, 7)) == 1
assert get_week_number(date(2024, 3, 29)) == 12
assert get_week_number(date(2024, 3, 31)) == 13
assert get_week_number(date(2024, 4, 14)) == 15
assert get_week_number(date(2024, 4, 13)) == 14

assert get_week_number(date(2023, 1, 1)) == 0
assert get_week_number(date(2023, 1, 2)) == 0
assert get_week_number(date(2023, 2, 28)) == 8
assert get_week_number(date(2023, 3, 5)) == 9

assert get_week_number(date(2024, 4, 14), start_date=date(2024, 4, 14)) == 0
assert get_week_number(date(2024, 4, 13), start_date=date(2024, 4, 14)) == -1

assert get_week_number(date(2025, 4, 13), start_date=date(2024, 4, 14)) == 52
# % ]

# get_patch_value(patch, date(2024, 4, 13)) == 0
# get_patch_value(patch, date(2024, 4, 14)) == 1
# get_patch_value(patch, date(2024, 4, 21)) == 0
# get_patch_value(patch, date(2024, 4, 23)) == 1

