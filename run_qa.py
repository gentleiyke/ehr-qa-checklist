from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

def parse_censored_age(value) -> Optional[int]:
    # Convert censored ages (89) into an integer cap (90)
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)) and not pd.isna(value):
        return int(value)

    s = str(value).strip()
    if s.startswith(">"):
        s2 = s.replace(">", "").strip()
        if s2.isdigit():
            return int(s2) + 1
        return None

    if s.isdigit():
        return int(s)

    return None


def iqr_flags(series: pd.Series, k: float = 1.5) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return pd.Series([False] * len(series), index=series.index)
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return (s < lower) | (s > upper)


def safe_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def summarise_missingness(df: pd.DataFrame) -> Dict[str, Any]:
    miss = df.isna().mean().sort_values(ascending=False)
    return {
        "overall_missing_rate": float(df.isna().mean().mean()),
        "missing_rate_by_column": {k: float(v) for k, v in miss.items()},
        "top_10_missing_columns": [
            {"column": k, "missing_rate": float(v)} for k, v in miss.head(10).items()
        ],
    }


def summarize_duplicates(df: pd.DataFrame, id_cols: Optional[List[str]] = None) -> Dict[str, Any]:
    out: Dict[str, Any] = {"duplicate_rows": int(df.duplicated().sum())}
    if id_cols:
        present = [c for c in id_cols if c in df.columns]
        if present:
            out["duplicate_by_id_cols"] = {
                "id_cols": present,
                "duplicate_count": int(df.duplicated(subset=present).sum()),
            }
    return out


def numeric_outlier_summary(df: pd.DataFrame, numeric_cols: List[str], k: float) -> Dict[str, Any]:
    results = {}
    for col in numeric_cols:
        if col not in df.columns:
            continue
        flags = iqr_flags(df[col], k=k)
        results[col] = {
            "outlier_count": int(flags.sum()),
            "outlier_rate": float(flags.mean()),
        }
    return results


def save_plots(df: pd.DataFrame, outdir: Path, time_col: Optional[str], age_col: Optional[str]) -> Dict[str, str]:
#    Saves PNGs if matplotlib is available; otherwise skips
    paths = {}
    try:
        import matplotlib.pyplot as plt  
    except Exception:
        return paths

    outdir.mkdir(parents=True, exist_ok=True)

    # Missingness bar (top 15)
    miss = df.isna().mean().sort_values(ascending=False).head(15)
    plt.figure()
    miss.plot(kind="bar")
    plt.title("Top 15 columns by missingness rate")
    plt.ylabel("Missingness rate")
    p = outdir / "missingness_top15.png"
    plt.tight_layout()
    plt.savefig(p)
    plt.close()
    paths["missingness_top15"] = str(p)

    # Age histogram
    if age_col and age_col in df.columns:
        age = pd.to_numeric(df[age_col], errors="coerce").dropna()
        if len(age) > 0:
            plt.figure()
            age.plot(kind="hist", bins=30)
            plt.title("Age distribution")
            plt.xlabel("Age")
            p = outdir / "age_hist.png"
            plt.tight_layout()
            plt.savefig(p)
            plt.close()
            paths["age_hist"] = str(p)

    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QA checks on an EHR-style CSV dataset.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--outdir", default="outputs", help="Output directory")
    parser.add_argument("--time-col", default=None, help="Name of datetime column")
    parser.add_argument("--age-col", default=None, help="Name of age column")
    parser.add_argument("--id-cols", default=None, help="Comma-separated identifier columns for duplicate checks")
    parser.add_argument("--outlier-cols", default=None, help="Comma-separated numeric columns to check outliers")
    parser.add_argument("--iqr-k", type=float, default=1.5, help="IQR multiplier (default: 1.5)")
    parser.add_argument("--save-plots", action="store_true", help="Save basic PNG plots (requires matplotlib)")
    args = parser.parse_args()

    in_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    # Basic dataset info
    report: Dict[str, Any] = {
        "input_file": str(in_path),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
    }

    # Missingness
    report["missingness"] = summarise_missingness(df)

    # Duplicate checks
    id_cols = [c.strip() for c in args.id_cols.split(",")] if args.id_cols else None
    report["duplicates"] = summarize_duplicates(df, id_cols=id_cols)

    # Age handling (censored values like >89)
    cleaned_df = df.copy()
    if args.age_col and args.age_col in cleaned_df.columns:
        cleaned_age = cleaned_df[args.age_col].apply(parse_censored_age)
        cleaned_df[args.age_col] = pd.to_numeric(cleaned_age, errors="coerce")
        report["age_handling"] = {
            "age_col": args.age_col,
            "num_missing_after_parse": int(pd.isna(cleaned_df[args.age_col]).sum()),
            "max_age_after_parse": (
                float(cleaned_df[args.age_col].max()) if cleaned_df[args.age_col].notna().any() else None
            ),
        }

    # Time features
    if args.time_col and args.time_col in cleaned_df.columns:
        s = cleaned_df[args.time_col].astype(str).str.strip()

        # Try HH:MM first
        t = pd.to_datetime(s, format="%H:%M", errors="coerce")

        # Fallback to HH:MM:SS if needed
        if t.isna().mean() > 0.2:
            t = pd.to_datetime(s, format="%H:%M:%S", errors="coerce")

        cleaned_df["hour_of_day"] = t.dt.hour

        report["time_features"] = {
            "time_col": args.time_col,
            "parsed_as": "time24",
            "num_invalid_time_values": int(t.isna().sum()),
            "hour_of_day_added": True,
        }



    # Outlier checks
    outlier_cols = [c.strip() for c in args.outlier_cols.split(",")] if args.outlier_cols else []
    numeric_cols = outlier_cols if outlier_cols else cleaned_df.select_dtypes(include="number").columns.tolist()
    report["outliers_iqr"] = numeric_outlier_summary(cleaned_df, numeric_cols=numeric_cols, k=args.iqr_k)

    # Save outputs
    cleaned_path = outdir / "ehr_cleaned.csv"
    cleaned_df.to_csv(cleaned_path, index=False)

    # Save per-column outlier flags for numeric columns
    flags_df = pd.DataFrame(index=cleaned_df.index)
    for col in numeric_cols:
        if col in cleaned_df.columns:
            flags_df[f"{col}_iqr_outlier"] = iqr_flags(cleaned_df[col], k=args.iqr_k)
    outlier_flags_path = outdir / "outlier_flags.csv"
    flags_df.to_csv(outlier_flags_path, index=False)

    report["outputs"] = {
        "cleaned_csv": str(cleaned_path),
        "outlier_flags_csv": str(outlier_flags_path),
    }

    # Optional plots
    if args.save_plots:
        report["plots"] = save_plots(cleaned_df, outdir, args.time_col, args.age_col)

    report_path = outdir / "qa_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"✅ QA complete. Report written to: {report_path}")


if __name__ == "__main__":
    main()