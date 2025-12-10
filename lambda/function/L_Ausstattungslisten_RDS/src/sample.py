import pandas as pd
import re
import os

file_path = "/Users/rakeshkumar/VisualStudioProjects/dom-basic-input-data-service/lambda/function/L_Ausstattungslisten_RDS/20240712_PASL_Export_C174_2024_805_055_row.csv"
file_name = os.path.basename(file_path)

# Extract model series from file name
parts = file_name.split("_")
model_series = parts[3]  # index 3 -> C174

# Read raw CSV without header
df_raw = pd.read_csv(file_path, header=None)

# Metadata rows
country_row = df_raw.iloc[0].replace(r'^\s*$', pd.NA, regex=True)  # normalize blanks to NaN
marketname_row = df_raw.iloc[1]

# Data starts from row 2
data = df_raw.iloc[2:].reset_index(drop=True)
data.columns = marketname_row

# Rename null columns to equipment levels
data = data.rename(columns={
    "null 1": "equipment_level_1",
    "null 2": "equipment_level_2",
    "null 3": "equipment_level_3"
})

# Static columns (A–O)
static_cols = data.columns[:15]

final_df = []

# ✅ Detect markets actually present
detected_markets = country_row[15:].dropna().unique().tolist()
print("Detected Market Codes:", detected_markets)

# 🚨 Column-level validation: ensure every column has a market code
for col_idx in range(15, len(data.columns)):
    country = country_row[col_idx]
    if pd.isna(country):   # missing
        raise ValueError(
            f"❌ Market Code is missing at column {col_idx} "
            f"(header: {marketname_row[col_idx]}) in file {file_name}"
        )

    raw_name = str(marketname_row[col_idx])

    # Extract bausatz (number in parentheses)
    bausatz_match = re.search(r"\((\d+)\)", raw_name)
    bausatz = bausatz_match.group(1) if bausatz_match else None

    # Extract market name (remove number prefix and parentheses)
    name_clean = re.sub(r"^\d+\)\s*", "", raw_name)
    name_clean = re.sub(r"\s*\(\d+\)\s*$", "", name_clean)

    temp_df = data[static_cols].copy()
    temp_df["Market Code"] = country
    temp_df["Vehicle Name"] = name_clean
    temp_df["Baumuster"] = bausatz
    temp_df["Legend"] = data.iloc[:, col_idx]
    final_df.append(temp_df)

# Merge
result_df = pd.concat(final_df, ignore_index=True)

# Add model series column
result_df["Model Series"] = model_series

# Save
result_df.to_excel(
    'output.xlsx',
    sheet_name='20240712_PMASL_Export_C174_2024_805_055_sample',
    index=False
)

print(result_df)
