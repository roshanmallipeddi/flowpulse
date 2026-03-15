from src.pipeline.pandas_etl import PandasETL
import pandas as pd

etl = PandasETL()

def test_clean_removes_dupes():

    df = pd.DataFrame({
        "event_id":[1,1,2],
        "geo_city":["NY","NY","LA"],
        "event_timestamp":["2024-01-01","2024-01-01","2024-01-01"]
    })

    df = etl.clean(df)

    assert len(df)==2
    
def test_clean_fills_nulls():

    df = pd.DataFrame({
        "event_id":[1],
        "geo_city":[None],
        "event_timestamp":["2024-01-01"]
    })

    df = etl.clean(df)

    assert df["geo_city"].iloc[0]=="Unknown"
    
def test_transform_adds_columns():

    df = pd.DataFrame({
        "event_id":[1],
        "user_id":["u1"],
        "session_id":["s1"],
        "geo_city":["NY"],
        "device_type":["mobile"],
        "event_timestamp":["2024-01-01"]
    })

    df = etl.clean(df)

    df = etl.transform(df)

    assert "hour_of_day" in df.columns
    assert "session_rank" in df.columns
    
def test_aggregate_correct_counts():

    df = pd.DataFrame({
        "event_id":[1,2],
        "user_id":["u1","u1"],
        "session_id":["s1","s2"],
        "device_type":["mobile","mobile"],
        "geo_city":["NY","NY"],
        "event_timestamp":["2024-01-01","2024-01-02"]
    })

    df = etl.clean(df)

    df = etl.transform(df)

    summary = etl.aggregate(df)

    assert summary["total_events"].iloc[0]==2
    
def test_pipeline_end_to_end():

    etl = PandasETL()

    etl.run_pipeline(
        "data/raw/sample_user_events.csv",
        "data/processed/test_output.parquet"
    )

    import os

    assert os.path.exists("data/processed/test_output.parquet")
    
def test_profile_returns_expected_keys():
    etl = PandasETL()

    df = pd.DataFrame({
        "event_id": [1, 2],
        "geo_city": ["NY", None],
        "event_timestamp": ["2024-01-01", "2024-01-02"]
    })

    profile = etl.profile(df, "TEST")

    assert "row_count" in profile
    assert "null_counts" in profile
    assert "unique_counts" in profile
    assert "numeric_min_max" in profile    