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
country_row = df_raw.iloc[0]
print("country_row: ", country_row)
marketname_row = df_raw.iloc[1]

# Data starts from row 2
data = df_raw.iloc[2:].reset_index(drop=True)
data.columns = marketname_row
# print(data.columns)

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

print("length: ",len(data.columns))
last_number = None
last_country = None

for col_idx in range(15, len(data.columns)):
    country = country_row[col_idx]
    raw_name = str(marketname_row[col_idx])

    # Extract the leading number (e.g. "7)" -> 7)
    num_match = re.match(r"(\d+)\)", raw_name.strip())
    num = int(num_match.group(1)) if num_match else None

    if pd.notna(country):  # New country starts
        if last_number is not None and num != 1:
            print(f"⚠️ Possible missing block before '{country}', "
                  f"expected restart at 1) but found {num})")
        last_country = country
        last_number = num
    else:
        # Same country, check continuity
        if last_number is not None and num is not None:
            if num != last_number + 1:
                print(f"⚠️ Missing sub-rows in '{last_country}': "
                      f"expected {last_number+1}) but got {num})")
        last_number = num


for col_idx in range(15, len(data.columns)):
    country = country_row[col_idx]
    # print("country: ", country)
    
    # 🚨 Raise exception if Market Code is missing
    if pd.isna(country):
        continue
        # raise ValueError(f"Market Code is missing at column index {col_idx} (header: {marketname_row[col_idx]})")
    
    if pd.notna(country):
        last_country = country
    else:
        # If missing but previous country exists, use carry forward
        country = last_country  
    
    raw_name = str(marketname_row[col_idx])
    # print("raw_name: ", raw_name)
    
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

# Add model series column
result_df["Model Series"] = model_series

# Save
result_df.to_excel('output.xlsx', sheet_name='20240712_PMASL_Export_C174_2024_805_055_sample', index=False)

# print(result_df)
