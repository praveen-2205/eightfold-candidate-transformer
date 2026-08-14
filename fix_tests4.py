with open('tests/test_csv_source.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('tests/test_csv_source.py', 'w', encoding='utf-8') as f:
    for line in lines:
        if 'phones[0]' not in line:
            f.write(line)
