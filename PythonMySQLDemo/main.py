import os
import re
import pandas as pd
import mysql.connector
from mysql.connector import Error

# -----------------------------
# Database Configuration
# -----------------------------
HOST = "localhost"
USER = "root"
PASSWORD = "Madhavi@4321"
DATABASE = "Madhavi"

# ==========================================================
# ROOT DIRECTORY (PROJECT ROOT)
# ==========================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================
# INPUT FILE (from data folder OR prepared SQL folder)
# ==========================================================

INPUT_FILE = os.path.join(
    ROOT_DIR,
    "data",
    "data_prepared_for_sql",
    "digital_payment_featured_data.csv"
)


# ==========================================================
# LOAD DATA
# ==========================================================

def load_csv(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")
    return pd.read_csv(file_path)

df = load_csv(INPUT_FILE)

print("✅ Loaded file:", INPUT_FILE)
print("Shape:", df.shape)


def sanitize_name(name):
    """
    Convert a filename or column name into a valid MySQL identifier.
    """
    name = os.path.splitext(name)[0]        # Remove .csv extension
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    return name


try:

    # Connect to MySQL
    connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

    cursor = connection.cursor()

    # Read CSV
    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df)} records.")

    # Generate table name from filename
    table_name = sanitize_name(os.path.basename(INPUT_FILE))

    print("Creating table:", table_name)

    # Build CREATE TABLE statement
    columns = []

    for column in df.columns:

        column_name = sanitize_name(column)

        # Store everything as TEXT for maximum compatibility
        columns.append(f"`{column_name}` TEXT")

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        {', '.join(columns)}
    )
    """

    cursor.execute(create_table_query)

    # Build INSERT statement
    column_names = [sanitize_name(col) for col in df.columns]

    insert_query = f"""
    INSERT INTO `{table_name}`
    ({','.join(f'`{c}`' for c in column_names)})
    VALUES ({','.join(['%s'] * len(column_names))})
    """

    records = []

    for _, row in df.iterrows():

        record = []

        for value in row:
            if pd.isna(value):
                record.append(None)
            else:
                record.append(str(value))

        records.append(tuple(record))

    cursor.executemany(insert_query, records)

    connection.commit()

    print("--------------------------------")
    print("Upload Successful")
    print("Table :", table_name)
    print("Rows  :", cursor.rowcount)
    print("--------------------------------")

except Error as e:
    print("Database Error:", e)

except FileNotFoundError:
    print("CSV file not found.")

finally:

    if 'cursor' in locals():
        cursor.close()

    if 'connection' in locals() and connection.is_connected():
        connection.close()

    print("Connection Closed.")