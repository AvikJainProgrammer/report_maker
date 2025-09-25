import pandas as pd
import pyodbc
import os
import yaml
from datetime import datetime
from tableimage import TableImage
from credentials import server, database, username, password

# Folders
QUERY_FOLDER = "queries"
OUTPUT_FOLDER = "output_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# DB connection
connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()

def read_yaml(filepath):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def generate_table_image(df, config, output_file):
    # --------------------------
    # 1. Apply dtypes if specified
    # --------------------------
    if "dtypes" in config:
        for col, dtype in config["dtypes"].items():
            try:
                df[col] = df[col].astype(dtype)
            except Exception:
                pass  # fallback if type casting fails

    # --------------------------
    # 2. Apply sorting
    # --------------------------
    if "sort" in config:
        for rule in config["sort"]:
            col = rule["column"]
            asc = rule.get("ascending", True)
            if col in df.columns:
                df = df.sort_values(by=col, ascending=asc, ignore_index=True)

    # --------------------------
    # 3. Create totals row
    # --------------------------
    numeric_cols = df.select_dtypes(include='number').columns
    totals = df[numeric_cols].sum().to_dict()
    totals_row = {col: totals.get(col, '') for col in df.columns}
    totals_row[df.columns[0]] = 'TOTAL'
    df_with_totals = pd.concat([pd.DataFrame([totals_row]), df], ignore_index=True)

    # --------------------------
    # 4. Formatting
    # --------------------------
    formatting = config.get("formatting", {})
    header_row_bg = formatting.get("header", {}).get("bg", "#333333")
    header_fg = formatting.get("header", {}).get("fg", "#ffffff")

    row_bg_dict = {}
    row_fg_dict = {}
    col_bg_dict = {}
    col_fg_dict = {}

    # Row formatting (e.g., TOTAL row)
    if "rows" in formatting:
        for key, style in formatting["rows"].items():
            # match by label in first col
            idx = df_with_totals.index[df_with_totals.iloc[:, 0] == key].tolist()
            for i in idx:
                if "bg" in style: row_bg_dict[i] = style["bg"]
                if "fg" in style: row_fg_dict[i] = style["fg"]

    # Column formatting
    if "columns" in formatting:
        for col, style in formatting["columns"].items():
            if col in df_with_totals.columns:
                j = df_with_totals.columns.get_loc(col)
                if "bg" in style: col_bg_dict[j] = style["bg"]
                if "fg" in style: col_fg_dict[j] = style["fg"]

    # --------------------------
    # 5. Render table
    # --------------------------
    table_img = TableImage(
        df_with_totals,
        heading=config["heading"].replace("{date}", datetime.today().strftime("%d-%b'%y")),
        heading_font_size=20,
        cell_font_size=16,
        cell_padding=10,
        header_row_bg=header_row_bg,
        header_fg=header_fg,
        row_bg_dict=row_bg_dict,
        row_fg_dict=row_fg_dict,
        column_bg=col_bg_dict,
        column_fg=col_fg_dict,
        border_color="black"
    )

    table_img.render(save_path=output_file)

def main():
    try:
        cnxn = pyodbc.connect(connection_string)
        print("Connection successful!")

        for filename in os.listdir(QUERY_FOLDER):
            if filename.endswith(".sql"):
                query_file = os.path.join(QUERY_FOLDER, filename)
                yaml_file = query_file.replace(".sql", ".yaml")

                query = read_file(query_file)
                config = read_yaml(yaml_file)

                df = pd.read_sql_query(query, cnxn)
                output_file = os.path.join(OUTPUT_FOLDER, filename.replace(".sql", ".png"))

                generate_table_image(df, config, output_file)

    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")

    finally:
        if 'cnxn' in locals() and cnxn:
            cnxn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()
