# 🏥 # EHR Data Quality Checklist (Notebook + CLI)

A practical data quality (QA) framework for Electronic Health Record (EHR) datasets, combining an exploratory Jupyter notebook with a reproducible command-line tool. This project focuses on identifying and documenting common data risks in healthcare datasets prior to analysis or modelling.

---

## Why This Project Exists

EHR datasets often appear analysis-ready but contain silent issues that can bias results or invalidate conclusions, including:
- systematic missingness
- censored clinical values (e.g. `>89` for age)
- inconsistent timestamps
- implausible measurements
- duplicate patient stays

The emphasis is on **governance, interpretability, and decision safety**.

---

## What’s Included

### 1) Exploratory Notebook
**`notebooks/ehr-qa-checklist.ipynb`**

The notebook demonstrates:
- missingness analysis and visualisation
- handling censored age values
- time-of-day feature engineering from EHR `*time24` fields
- IQR-based outlier flagging (outliers flagged, not dropped)
- interpretation of anomalies in a healthcare context

This notebook is intended for:
- exploration
- validation
- documentation of assumptions

---

### 2) Reproducible CLI Tool
**`run_qa.py`**

The CLI turns the notebook logic into a reusable QA utility that can be run on any EHR-style CSV.

It produces:
- a structured JSON QA report
- a cleaned dataset
- per-column outlier flags
- optional QA plots

---

## Quickstart (CLI)

### Requirements
- Python 3.10+
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Run QA checks
```
python run_qa.py \
  --input data/EHR.csv \
  --outdir outputs \
  --age-col age \
  --time-col hospitaladmittime24 \
  --id-cols uniquepid,patientunitstayid,patienthealthsystemstayid \
  --outlier-cols admissionheight,admissionweight,dischargeweight,hospitaladmitoffset,hospitaldischargeoffset,unitdischargeoffset \
  --save-plots
```
