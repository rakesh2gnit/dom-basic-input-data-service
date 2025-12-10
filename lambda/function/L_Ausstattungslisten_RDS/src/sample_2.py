import pandas as pd
import re
import os

file_path = "/Users/rakeshkumar/VisualStudioProjects/dom-basic-input-data-service/lambda/function/L_Ausstattungslisten_RDS/20240712_PASL_Export_C174_2024_805_055_for_database_sample_data.csv"
file_name = os.path.basename(file_path)

# Extract model series from file name
parts = file_name.split("_")
model_series = parts[3]  # index 3 -> C174

# Read raw CSV without header
df_raw = pd.read_csv(file_path, header=None)

# Metadata rows
country_row = df_raw.iloc[0]
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

last_country = None

for col_idx in range(15, len(data.columns)):
    country = country_row[col_idx]
    if pd.notna(country):
        last_country = country
    else:
        country = last_country  # carry forward last country if missing
    raw_name = str(marketname_row[col_idx])
    
    # Extract bausatz (number in parentheses)
    bausatz_match = re.search(r"\((\d+)\)", raw_name)
    bausatz = bausatz_match.group(1) if bausatz_match else None
    
    # Extract market name (remove number prefix and parentheses)
    name_clean = re.sub(r"^\d+\)\s*", "", raw_name)  # remove "1) "
    name_clean = re.sub(r"\s*\(\d+\)\s*$", "", name_clean)  # remove "(174311)"
    
    if pd.notna(country) and pd.notna(raw_name):
        temp_df = data[static_cols].copy()
        temp_df["Market Code"] = country
        temp_df["Vehicle Name"] = name_clean
        temp_df["Baumuster"] = bausatz
        temp_df["Legend"] = data.iloc[:, col_idx]
        final_df.append(temp_df)

# Merge
result_df = pd.concat(final_df, ignore_index=True)
result_df.to_excel('output.xlsx', sheet_name='20240712_PMASL_Export_C174_2024_805_055_sample', index=False)

# Add model series column
result_df["Model Series"] = model_series

print(result_df)

# Example output for WEU
# print(result_df[result_df["Market Code"] == "WEU"].head(10))
# print(result_df.info())
