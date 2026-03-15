import pandas as pd
import time
import os


class PandasETL:

    def read_raw(self, filepath):
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith(".json"):
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")

        print("Rows:", df.shape[0])
        print("Columns:", df.shape[1])
        print("Dtypes:")
        print(df.dtypes)

        return df

    def profile(self, df, label):
        print(f"\n--- DATA PROFILE: {label} ---")

        row_count = len(df)
        null_counts = df.isna().sum()
        unique_counts = df.nunique(dropna=False)

        numeric_cols = df.select_dtypes(include="number")
        numeric_min_max = (
            numeric_cols.agg(["min", "max"]) if not numeric_cols.empty else pd.DataFrame()
        )

        print("Row count:", row_count)

        print("\nNull counts:")
        print(null_counts)

        print("\nUnique counts:")
        print(unique_counts)

        if not numeric_min_max.empty:
            print("\nNumeric min/max:")
            print(numeric_min_max)
        else:
            print("\nNumeric min/max: No numeric columns found")

        return {
            "row_count": row_count,
            "null_counts": null_counts,
            "unique_counts": unique_counts,
            "numeric_min_max": numeric_min_max,
        }

    def compare_profiles(self, before_profile, after_profile):
        print("\n=== BEFORE vs AFTER CLEANING COMPARISON ===")

        print("\nRow count comparison:")
        row_comparison = pd.DataFrame({
            "before": [before_profile["row_count"]],
            "after": [after_profile["row_count"]],
            "difference": [after_profile["row_count"] - before_profile["row_count"]]
        }, index=["row_count"])
        print(row_comparison)

        print("\nNull count comparison:")
        null_comparison = pd.DataFrame({
            "before": before_profile["null_counts"],
            "after": after_profile["null_counts"]
        })
        null_comparison["difference"] = null_comparison["after"] - null_comparison["before"]
        print(null_comparison)

        print("\nUnique count comparison:")
        unique_comparison = pd.DataFrame({
            "before": before_profile["unique_counts"],
            "after": after_profile["unique_counts"]
        })
        unique_comparison["difference"] = unique_comparison["after"] - unique_comparison["before"]
        print(unique_comparison)

        before_numeric = before_profile["numeric_min_max"]
        after_numeric = after_profile["numeric_min_max"]

        if not before_numeric.empty or not after_numeric.empty:
            print("\nNumeric min/max comparison:")
            numeric_comparison = pd.concat(
                {"before": before_numeric, "after": after_numeric},
                axis=1
            )
            print(numeric_comparison)
        else:
            print("\nNumeric min/max comparison: No numeric columns found")

    def clean(self, df):
        df = df.drop_duplicates(subset=["event_id"])
        df["geo_city"] = df["geo_city"].fillna("Unknown")
        df["event_timestamp"] = pd.to_datetime(df["event_timestamp"])
        now = pd.Timestamp.now()
        df = df[df["event_timestamp"] <= now]
        return df

    def transform(self, df):
        df = df.sort_values(["user_id", "session_id", "event_timestamp"])

        df["hour_of_day"] = df["event_timestamp"].dt.hour
        df["is_weekend"] = df["event_timestamp"].dt.dayofweek >= 5
        df["session_rank"] = (
            df.groupby(["user_id", "session_id"])["event_timestamp"]
            .rank(method="first")
            .astype(int)
        )

        return df

    def aggregate(self, df):
        summary = df.groupby("user_id").agg(
            total_events=("event_id", "count"),
            unique_sessions=("session_id", "nunique"),
            first_event_date=("event_timestamp", "min"),
            last_event_date=("event_timestamp", "max")
        ).reset_index()

        device = (
            df.groupby("user_id")["device_type"]
            .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown")
            .reset_index()
            .rename(columns={"device_type": "most_common_device"})
        )

        summary = summary.merge(device, on="user_id", how="left")
        return summary

    def write_output(self, df, filepath, format="parquet"):
        if format == "parquet":
            df.to_parquet(filepath, index=False)
        else:
            df.to_csv(filepath, index=False)

        size = os.path.getsize(filepath)

        print("Rows written:", len(df))
        print("File size:", size)

    def run_pipeline(self, input_path, output_path):
        start = time.time()

        df = self.read_raw(input_path)

        before_profile = self.profile(df, "BEFORE CLEAN")

        df = self.clean(df)

        after_profile = self.profile(df, "AFTER CLEAN")

        self.compare_profiles(before_profile, after_profile)

        df = self.transform(df)

        summary = self.aggregate(df)

        self.write_output(summary, output_path)

        end = time.time()

        print("\nPipeline runtime:", round(end - start, 2), "seconds")


if __name__ == "__main__":
    etl = PandasETL()
    etl.run_pipeline(
        "data/raw/sample_user_events.csv",
        "data/processed/user_event_summary.parquet"
    )