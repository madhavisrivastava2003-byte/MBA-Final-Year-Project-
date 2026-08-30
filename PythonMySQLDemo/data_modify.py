import os
import pandas as pd
import numpy as np

# ==========================================================
# FILE PATHS
# ==========================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CLEAN_DATA_FOLDER = os.path.join(ROOT_DIR, "data", "clean_up_data")

INPUT_FILE = os.path.join(
    CLEAN_DATA_FOLDER,
    "Clean_Digital_Payment_Survey.csv"
)

FEATURE_DATA_FOLDER = os.path.join(
    ROOT_DIR,
    "data",
    "data_prepared_for_sql"
)

os.makedirs(FEATURE_DATA_FOLDER, exist_ok=True)

OUTPUT_FILE = os.path.join(
    FEATURE_DATA_FOLDER,
    "digital_payment_featured_data.csv"
)

print("📌 ROOT_DIR:", ROOT_DIR)
print("📥 INPUT_FILE:", INPUT_FILE)
print("📤 OUTPUT_FILE:", OUTPUT_FILE)


# ==========================================================
# STEP 1: LOAD DATA
# ==========================================================

def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    return pd.read_csv(file_path)

df = load_dataset(INPUT_FILE)
print(f"✅ Loaded data: {df.shape}")


# ==========================================================
# STEP 2: CLEANING (SAFE + NON-DESTRUCTIVE)
# ==========================================================

df_clean = df.copy()

# Standardize column names
df_clean.columns = (
    df_clean.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# Remove duplicates
df_clean = df_clean.drop_duplicates()

# ----------------------------------------------------------
# SAFE MISSING VALUE HANDLING (TYPE-AWARE)
# ----------------------------------------------------------

for col in df_clean.columns:

    # Object columns
    if df_clean[col].dtype == "object":
        df_clean[col] = df_clean[col].fillna("Unknown")

    # Numeric columns ONLY if already numeric
    elif pd.api.types.is_numeric_dtype(df_clean[col]):
        df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    # Everything else (rare edge cases)
    else:
        df_clean[col] = df_clean[col].astype(str).fillna("Unknown")


print("🧹 Cleaning completed safely")


# ==========================================================
# STEP 3: FEATURE ENGINEERING
# ==========================================================


# ----------------------------------------------------------
# 1. HIGH SATISFACTION (FIXED LOGIC)
# Rating mapping:
# 5–3 = High
# 2 = Medium
# 1 = Low
# ----------------------------------------------------------

rating_cols = [c for c in df_clean.columns if "rating" in c or "satisfaction" in c]

if rating_cols:
    rating_col = rating_cols[0]

    df_clean[rating_col] = pd.to_numeric(df_clean[rating_col], errors="coerce")

    def rating_category(x):
        if pd.isna(x):
            return "Unknown"
        elif x >= 3:
            return "High"
        elif x == 2:
            return "Medium"
        else:
            return "Low"

    df_clean["satisfaction_level"] = df_clean[rating_col].apply(rating_category)
else:
    df_clean["satisfaction_level"] = "Unknown"


# ----------------------------------------------------------
# 2. FREQUENT USER (SAFE STRING HANDLING)
# ----------------------------------------------------------

usage_cols = [c for c in df_clean.columns if any(k in c for k in ["usage", "frequency", "transaction"])]

if usage_cols:
    usage_col = usage_cols[0]

    def freq_map(val):
        val = str(val).lower()
        if "daily" in val or "weekly" in val:
            return "Yes"
        return "No"

    df_clean["frequent_user"] = df_clean[usage_col].apply(freq_map)
else:
    df_clean["frequent_user"] = "No"


# ----------------------------------------------------------
# 3. CHURN INTENTION (FIXED SAFE LOGIC)
# ----------------------------------------------------------

def churn_logic(row):
    score = 0

    if row.get("satisfaction_level") in ["Low", "Medium"]:
        score += 1

    if row.get("frequent_user") == "No":
        score += 1

    for col in df_clean.columns:
        if any(x in col for x in ["feedback", "comment", "review"]):
            val = str(row[col]).lower()
            if any(word in val for word in ["bad", "poor", "issue", "problem", "difficult", "slow"]):
                score += 1

    return "Yes" if score >= 2 else "No"


df_clean["churn_intention"] = df_clean.apply(churn_logic, axis=1)


# ----------------------------------------------------------
# 4. DIGITAL ADOPTION LEVEL
# ----------------------------------------------------------

def adoption_level(row):
    if row.get("frequent_user") == "Yes" and row.get("satisfaction_level") == "High":
        return "High"
    elif row.get("frequent_user") == "Yes":
        return "Medium"
    else:
        return "Low"


df_clean["digital_adoption_level"] = df_clean.apply(adoption_level, axis=1)


# ----------------------------------------------------------
# 5. RISK SEGMENT
# ----------------------------------------------------------

def risk_segment(row):
    if row.get("churn_intention") == "Yes":
        return "High Risk"
    elif row.get("satisfaction_level") == "Low":
        return "Medium Risk"
    else:
        return "Low Risk"


df_clean["risk_segment"] = df_clean.apply(risk_segment, axis=1)


# ----------------------------------------------------------
# 6. CUSTOMER VALUE SCORE
# ----------------------------------------------------------

def value_score(row):
    score = 0

    if row.get("satisfaction_level") == "High":
        score += 2

    if row.get("frequent_user") == "Yes":
        score += 2

    if row.get("churn_intention") == "No":
        score += 1

    return score


df_clean["customer_value_score"] = df_clean.apply(value_score, axis=1)


print("✅ Feature engineering completed")


# ==========================================================
# STEP 4: FINAL VALIDATION
# ==========================================================

print("📊 Shape:", df_clean.shape)
print("\nNull values:\n", df_clean.isnull().sum())


# ==========================================================
# STEP 5: SAVE OUTPUT
# ==========================================================

df_clean.to_csv(OUTPUT_FILE, index=False)

print(f"💾 Saved successfully: {OUTPUT_FILE}")
print("🎯 Pipeline completed safely")