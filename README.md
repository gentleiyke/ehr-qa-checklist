# 🏥 EHR Data Quality & Patient Flow QA Checklist

## Overview
This repository contains a **Jupyter notebook demonstrating a practical data quality (QA) workflow for Electronic Health Record (EHR)–style datasets**.

Rather than jumping straight into modelling, this project focuses on **trust-building steps that must happen first** in healthcare analytics:
- missingness assessment
- domain-aware data cleaning
- time feature engineering
- outlier quality assurance

The notebook is designed to reflect **real-world healthcare analytics practices**, where data quality issues are often silent but impactful.

---

## Why This Project Matters
In healthcare, analytics failures rarely come from “bad models.”  
They come from **data that looks good enough but isn’t trustworthy**.

This notebook shows how to:
- detect workflow-driven missingness
- handle censored clinical fields (e.g. age values like `>89`)
- engineer time-based patient flow features
- treat outliers as clinical signals, not automatic errors

The emphasis is on **governance, interpretability, and decision safety**.

---

## Dataset Context
- **Type:** Simulated / de-identified patient encounter data  
- **Granularity:** Encounter-level (not patient-level)  
- **Domain:** Admissions, unit transfers, demographics, timestamps  

> ⚠️ No real patient-identifiable data is included.

---

## Key Steps in the Notebook
1. **Initial data inspection**
   - Shape, data types, required fields
2. **Missingness audit**
   - Quantitative summaries
   - Visual missingness matrix
3. **Domain-aware cleaning**
   - Safe handling of censored ages (`>89`)
4. **Patient flow feature engineering**
   - Timestamp parsing
   - Hour-of-day extraction
5. **Exploratory analysis**
   - Distributions and correlations
6. **Outlier QA**
   - IQR-based flagging (not blind removal)
7. **Reusable QA summary**
   - Consolidated reporting for repeat use

---

## Skills Demonstrated
- Healthcare data quality assessment
- EHR-specific data cleaning
- Patient flow analytics
- Reusable analytics functions
- Governance-aware analytical thinking
- Clear technical communication

---

## Who This Is For
- Healthcare analysts and BI professionals
- Data scientists working with EHR or operational data
- Beginners transitioning into healthcare analytics
- Recruiters reviewing real-world portfolio work

---

## How to Run the Notebook
1. Clone this repository
2. Install dependencies (example):
   ```bash
   pip install pandas numpy matplotlib seaborn missingno
