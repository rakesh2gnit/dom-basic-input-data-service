import pandas as pd
import numpy as np

def data_transform(df, sheet, column_templates):
    
    df.columns = df.columns.str.strip()  # Strip whitespace from column names

    df.rename(columns=column_templates, inplace=True)

    df.drop_duplicates(inplace=True)  # Remove duplicate rows

    key_colummns = ['sales_name','baumuster']

    df = df.dropna(how='all')  # Drop rows where all key columns are NaN

    df.replace({np.nan: None, pd.NaT: None}, inplace=True)  # Replace NaN and NaT with None

    if sheet:
        color_check = []
        for row in sheet.iterrows(min_row = 2, max_row = df.shape[0] + 1):
            cell = row[2]
            if cell.font.color:
                font_color = cell.font.color.rgb
            else:
                font_color = None

            if font_color == 'FF00B050':  # Check if the font color is red
                color_check.append(2)
            elif font_color in ('FFFF0000', 'FFC00000'):
                color_check.append(1)
            else:
                color_check.append(3)
            

        df['status'] = color_check
        df['status'] = pd.to_numeric(df['status'], errors='coerce').astype('int')  # Convert to numeric, coercing errors

    df['key'] = df.apply(lambda row: "_".join(map(str, [row[col] for col in key_colummns])), axis=1)

    return df