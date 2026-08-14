import os

# 1. Update test_normalize_phones.py to test the strict policy
phone_test = '''
from candidate_transformer.normalize import to_e164

def test_phones_strict_no_guess():
    # Should NOT guess +1 when country code is missing
    assert to_e164("(415) 555-0123") is None
    assert to_e164("6369821425") is None

def test_phones_with_country_code():
    # Should work when country code is explicit
    assert to_e164("+1 (415) 555-0123") == "+14155550123"
    assert to_e164("+91 98765 43210") == "+919876543210"
'''
with open('tests/test_normalize_phones.py', 'w', encoding='utf-8') as f:
    f.write(phone_test)

# 2. Update test_projection.py mock data to have a valid international number
with open('tests/test_projection.py', 'r', encoding='utf-8') as f:
    proj_test = f.read()
proj_test = proj_test.replace('"4155550123"', '"+14155550123"')
with open('tests/test_projection.py', 'w', encoding='utf-8') as f:
    f.write(proj_test)

# 3. Update test_csv_source.py (The sample CSV phone lacks a country code, so it should be dropped)
with open('tests/test_csv_source.py', 'r', encoding='utf-8') as f:
    csv_test = f.read()
csv_test = csv_test.replace('assert len(phones) == 1', 'assert len(phones) == 0  # Strict policy: dropped missing country code')
with open('tests/test_csv_source.py', 'w', encoding='utf-8') as f:
    f.write(csv_test)
