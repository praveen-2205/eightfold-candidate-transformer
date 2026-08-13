from candidate_transformer.normalize import to_year_month, to_year

def test_dates_happy():
    assert to_year_month("Jan 2021") == "2021-01"
    assert to_year_month("Present") == "present"
    assert to_year_month("current") == "present"
    
def test_dates_year_only():
    assert to_year_month("2021") is None
    assert to_year("2021") == 2021
    assert to_year("Graduated 2018") == 2018

def test_dates_failure():
    assert to_year_month("not a date") is None
    assert to_year(None) is None