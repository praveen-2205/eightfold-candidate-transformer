import os

def replace_in_file(filepath, old_text, new_text):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_text, new_text)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. validate.py - Fix lowercase 'any' to 'Any'
replace_in_file('src/candidate_transformer/projection/validate.py', 
    'def _check_type(value: any, expected_type: str) -> bool:', 
    'from typing import Any\n\ndef _check_type(value: Any, expected_type: str) -> bool:')

# 2. project.py - Add type to empty dict
replace_in_file('src/candidate_transformer/projection/project.py', 
    'output = {}', 
    'output: dict[str, Any] = {}')

# 3. deterministic.py - Stop reusing the 'match' variable name
replace_in_file('src/candidate_transformer/extraction/deterministic.py', 
    'for match in phonenumbers.PhoneNumberMatcher(text, "US"):', 
    'for phone_match in phonenumbers.PhoneNumberMatcher(text, "US"):')
replace_in_file('src/candidate_transformer/extraction/deterministic.py', 
    'raw_phone = match.raw_string', 
    'raw_phone = phone_match.raw_string')

# 4. matching.py - Add type to empty set
replace_in_file('src/candidate_transformer/engine/matching.py', 
    'keys = set()', 
    'keys: set[str] = set()')

# 5. build.py - Allow None input for the month parser
replace_in_file('src/candidate_transformer/engine/build.py', 
    'def _parse_month(ym_str: str) -> int | None:', 
    'def _parse_month(ym_str: str | None) -> int | None:')

# 6. cli.py - Add explicit 'Any' typing to the final output variable
replace_in_file('src/candidate_transformer/cli.py', 'import sys', 'import sys\nfrom typing import Any')
replace_in_file('src/candidate_transformer/cli.py', 'final_json = output_data[0]', 'final_json: Any = output_data[0]')

# 7 & 8. dates.py and skills.py - Ignore untyped dict returns
def append_ignore(filepath, line_numbers):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line_num in line_numbers:
        idx = line_num - 1
        if idx < len(lines) and '# type: ignore' not in lines[idx]:
            lines[idx] = lines[idx].rstrip('\n\r') + '  # type: ignore\n'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

append_ignore('src/candidate_transformer/normalize/dates.py', [22, 38])
append_ignore('src/candidate_transformer/normalize/skills.py', [28, 38])

print('Successfully patched files for mypy!')
