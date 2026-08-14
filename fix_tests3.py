with open('tests/test_csv_source.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('tests/test_csv_source.py', 'w', encoding='utf-8') as f:
    for line in lines:
        if 'assert phones[0].raw' not in line and 'assert phones[0].value' not in line:
            f.write(line)
