import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
from pandas.plotting import table
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
from tableimage import TableImage
from credentials import server, database, username, password




# SQL Server connection details
# server = 'libdata.c6rymyb13gs0.us-east-1.rds.amazonaws.com'
# database = 'libdata'
# username = 'avik_jain'
# password = 'libas123'

connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

# Folder containing queries and messages
QUERY_FOLDER = "queries"
OUTPUT_FOLDER = "output_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def read_file(filepath):
    with open(filepath, "r") as f:
        return f.read()

def generate_table_image(df, header_text, output_file):

    # --------------------------
    # 1. Create totals row
    # --------------------------
    numeric_cols = df.select_dtypes(include='number').columns
    totals = df[numeric_cols].sum().to_dict()
    totals_row = {col: totals.get(col, '') for col in df.columns}
    # Assume first column is non-numeric label
    totals_row[df.columns[0]] = 'TOTAL'
    df_with_totals = pd.concat([pd.DataFrame([totals_row]), df], ignore_index=True)

    # --------------------------
    # 2. Determine row and cell styling
    # --------------------------
    totals_row_index = 0  # Since totals row is at the top

    # Row-specific background and foreground
    row_bg_dict = {totals_row_index: "#800080"}  # purple
    row_fg_dict = {totals_row_index: "#ffffff"}  # white text

    # Header styling
    header_row_bg = "#333333"  # dark grey
    header_fg = "#ffffff"

    # --------------------------
    # 3. Generate table image
    # --------------------------
    table_img = TableImage(
        df_with_totals,
        heading=header_text,
        heading_font_size=20,  # bigger heading
        cell_font_size=16,
        cell_padding=10,
        header_row_bg=header_row_bg,
        header_fg=header_fg,
        row_bg_dict=row_bg_dict,
        row_fg_dict=row_fg_dict,
        border_color="black"
    )

    table_img.render(save_path=output_file)



def main():
    try:
        cnxn = pyodbc.connect(connection_string)
        print("Connection successful!")

        # Loop through all queries
        for filename in os.listdir(QUERY_FOLDER):
            if filename.endswith(".sql"):
                query_file = os.path.join(QUERY_FOLDER, filename)
                msg_file = query_file.replace(".sql", ".txt")

                query = read_file(query_file)
                msg_template = read_file(msg_file)

                # Replace date placeholder
                today_str = datetime.today().strftime("%d-%b'%y")
                header_text = msg_template.replace("{date}", today_str)

                # Execute query
                df = pd.read_sql_query(query, cnxn)

                # Output image file name
                output_file = os.path.join(OUTPUT_FOLDER, filename.replace(".sql", ".png"))

                # Generate table image
                generate_table_image(df, header_text, output_file)

    except pyodbc.Error as ex:
        print(f"Connection failed: {ex}")

    finally:
        if 'cnxn' in locals() and cnxn:
            cnxn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()
