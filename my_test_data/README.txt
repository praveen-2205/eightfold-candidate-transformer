Eightfold Recruiter CSV test cases

The structured company column is named latest_company instead of current_company.

Schema:
name,email,phone,latest_company,title

01_baseline_all_6.csv - normal matching case
02_conflicting_values.csv - intentional conflicts
03_missing_values.csv - missing fields
04_duplicate_records.csv - duplicate records
05_ambiguous_matching.csv - weak/ambiguous matching
