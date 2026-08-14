import os

cli_path = 'src/candidate_transformer/cli.py'
with open(cli_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find 'import sys' and inject dotenv right below it
if 'load_dotenv' not in content:
    content = content.replace('import sys', 'import sys\nfrom dotenv import load_dotenv\nload_dotenv()')
    with open(cli_path, 'w', encoding='utf-8') as f:
        f.write(content)
print('Successfully and safely patched cli.py!')
