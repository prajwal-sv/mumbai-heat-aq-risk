import pandas as pd
import pytest

@pytest.fixture(scope="module")
def df():
    return pd.read_csv("data/clean/daily_clean_final.csv")

def test_no_duplicate_days(df):
    assert df.duplicated(["station", "variable", "date_ist"]).sum() == 0

def test_pm_values_are_possible(df):
    pm = df[df["variable"].isin(["pm25", "pm10"])]["clean_value"].dropna()
    assert (pm > 0).all() and (pm <= 1000).all()

def test_temperature_values_in_range(df):
    t = df[df["variable"] == "temperature"]["clean_value"].dropna()
    assert t.between(10, 45).all()

def test_suspect_and_low_coverage_days_are_blank(df):
    bad = df[df["suspect"] | ~df["usable"]]
    assert bad["clean_value"].isna().all()

def test_comparison_table_has_all_models():
    t = pd.read_csv("models_saved/model_comparison.csv")
    for station, group in t.groupby("station"):
        assert set(group["model"]) == {"baseline", "linear", "forest"}