"""
Project Title:
Consumer Adoption and Satisfaction of Digital Payment Applications

File:
data_cleaning.py

Description:
This script performs data cleaning on the survey dataset collected in Excel.
It removes duplicates, handles missing values, standardizes text values,
creates age groups, and saves the cleaned dataset for further analysis.

Author: MBA Student
"""

import os
import numpy as np
import pandas as pd


# ==========================================================
# File Paths
# ==========================================================

# Root directory (where data_cleaning.py is located)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Input Folder
RAW_DATA_FOLDER = os.path.join(ROOT_DIR, "data", "raw_survey_data")

# Output Folder
CLEAN_DATA_FOLDER = os.path.join(ROOT_DIR, "data", "clean_up_data")

# Input Excel File
INPUT_FILE = os.path.join(
    RAW_DATA_FOLDER,
    "Digital_Payment_Survey.csv"
)

# Create Output Folder if it doesn't exist
os.makedirs(CLEAN_DATA_FOLDER, exist_ok=True)

# Output Excel File
OUTPUT_FILE = os.path.join(
    CLEAN_DATA_FOLDER,
    "Clean_Digital_Payment_Survey.csv"
)


# ==========================================================
# Create Output Folder
# ==========================================================

os.makedirs(CLEAN_DATA_FOLDER, exist_ok=True)


# ==========================================================
# Function to Standardize Payment App Names
# ==========================================================

def standardize_payment_app(app):

    if pd.isna(app):
        return np.nan

    app = str(app).strip().lower()

    mapping = {
        "google pay": "Google Pay",
        "googlepay": "Google Pay",
        "gpay": "Google Pay",
        "g pay": "Google Pay",

        "phonepe": "PhonePe",
        "phone pe": "PhonePe",

        "paytm": "Paytm",
        "pay tm": "Paytm",

        "amazon pay": "Amazon Pay",
        "amazonpay": "Amazon Pay",

        "bhim": "BHIM",

        "cred": "Cred",

        "mobikwik": "Mobikwik",
        "mobi kwik": "Mobikwik",

        "freecharge": "Freecharge",
        "free charge": "Freecharge"
    }

    return mapping.get(app, app.title())


# ==========================================================
# Function to Create Age Groups
# ==========================================================

def age_group(age):

    try:
        age = float(age)

        if age < 18:
            return "Below 18"

        elif age <= 25:
            return "18-25"

        elif age <= 35:
            return "26-35"

        elif age <= 45:
            return "36-45"

        elif age <= 60:
            return "46-60"

        else:
            return "Above 60"

    except:
        return "Unknown"


# ==========================================================
# Main Function
# ==========================================================

def main():

    try:

        print("=" * 60)
        print("LOADING DATA")
        print("=" * 60)

        # Read Excel File
        df = pd.read_csv(INPUT_FILE)

        original_records = len(df)

        print("\nFirst Five Rows")
        print(df.head())

        print("\nDataset Shape")
        print(df.shape)

        print("\nColumn Names")
        print(df.columns.tolist())

        print("\nData Types")
        print(df.dtypes)

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("CHECKING MISSING VALUES")
        print("=" * 60)

        print(df.isnull().sum())

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("REMOVING DUPLICATES")
        print("=" * 60)

        before_duplicates = len(df)

        df.drop_duplicates(inplace=True)

        after_duplicates = len(df)

        duplicates_removed = before_duplicates - after_duplicates

        print(f"Duplicates Removed : {duplicates_removed}")

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("REMOVING INCOMPLETE SURVEYS")
        print("=" * 60)

        important_columns = [
            "Age",
            "Gender",
            "Occupation",
            "Preferred Payment App",
            "Satisfaction Level"
        ]

        existing_columns = [
            col for col in important_columns
            if col in df.columns
        ]

        before_rows = len(df)

        if existing_columns:
            df.dropna(subset=existing_columns, inplace=True)

        after_rows = len(df)

        incomplete_removed = before_rows - after_rows

        print(f"Incomplete Surveys Removed : {incomplete_removed}")

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("REMOVING EXTRA SPACES")
        print("=" * 60)

        object_columns = df.select_dtypes(include="object").columns

        for col in object_columns:
            df[col] = df[col].astype(str).str.strip()

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("STANDARDIZING TEXT")
        print("=" * 60)

        if "Gender" in df.columns:
            df["Gender"] = df["Gender"].str.title()

        if "Occupation" in df.columns:
            df["Occupation"] = df["Occupation"].str.title()

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("STANDARDIZING PAYMENT APP NAMES")
        print("=" * 60)

        if "Preferred Payment App" in df.columns:
            df["Preferred Payment App"] = (
                df["Preferred Payment App"]
                .apply(standardize_payment_app)
            )

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("CREATING AGE GROUPS")
        print("=" * 60)

        if "Age" in df.columns:
            df["Age Group"] = df["Age"].apply(age_group)

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("HANDLING MISSING VALUES")
        print("=" * 60)

        # Numeric Columns
        numeric_columns = df.select_dtypes(include=np.number).columns

        for col in numeric_columns:
            df[col].fillna(df[col].median(), inplace=True)

        # Categorical Columns
        categorical_columns = df.select_dtypes(include="object").columns

        for col in categorical_columns:

            mode = df[col].mode()

            if len(mode) > 0:
                df[col].fillna(mode[0], inplace=True)
            else:
                df[col].fillna("Unknown", inplace=True)

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("VALIDATION")
        print("=" * 60)

        print("\nMissing Values After Cleaning\n")
        print(df.isnull().sum())

        cleaned_records = len(df)

        # --------------------------------------------------

        print("\nSaving Clean Dataset...")

        df.to_csv(OUTPUT_FILE, index=False)

        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("DATA CLEANING COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(f"Original Records           : {original_records}")
        print(f"Records After Cleaning     : {cleaned_records}")
        print(f"Duplicates Removed         : {duplicates_removed}")
        print(f"Incomplete Surveys Removed : {incomplete_removed}")

        print("\nRemaining Missing Values")
        print(df.isnull().sum().sum())

        print(f"\nClean dataset saved successfully at:\n{OUTPUT_FILE}")

    except FileNotFoundError:
        print("\nERROR: Excel file not found.")
        print(f"Expected location: {INPUT_FILE}")

    except PermissionError:
        print("\nERROR: Please close the Excel file before running the script.")

    except Exception as e:
        print("\nUnexpected Error:")
        print(e)


# ==========================================================
# Run Script
# ==========================================================

if __name__ == "__main__":
    main()