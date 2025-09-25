from PIL import Image, ImageDraw, ImageFont
import pandas as pd

class TableImage:
    def __init__(self, df, heading=None, heading_font_size=36, cell_font_size=16,
                 cell_padding=10, header_bg="#cccccc", row_bg="#ffffff", border_color="black",
                 column_bg=None, row_bg_dict=None, header_row_bg=None,
                 column_fg=None, row_fg_dict=None, cell_fg=None, header_fg="black"):
        """
        df: pandas DataFrame
        heading: optional heading text
        heading_font_size: int
        cell_font_size: int
        cell_padding: int
        header_bg: default header background
        row_bg: default row background
        border_color: border color
        column_bg: dict col_index -> bg color
        row_bg_dict: dict row_index -> bg color
        header_row_bg: header row bg color
        column_fg: dict col_index -> text color
        row_fg_dict: dict row_index -> text color
        cell_fg: dict (row_index, col_index) -> text color
        header_fg: header row text color
        """
        self.df = df
        self.heading = heading
        self.heading_font_size = heading_font_size
        self.cell_font_size = cell_font_size
        self.cell_padding = cell_padding
        self.header_bg = header_bg
        self.row_bg = row_bg
        self.border_color = border_color
        self.column_bg = column_bg or {}
        self.row_bg_dict = row_bg_dict or {}
        self.header_row_bg = header_row_bg or header_bg
        self.column_fg = column_fg or {}
        self.row_fg_dict = row_fg_dict or {}
        self.cell_fg = cell_fg or {}
        self.header_fg = header_fg
        
        # Fonts
        try:
            self.heading_font = ImageFont.truetype("arial.ttf", heading_font_size)
            self.cell_font = ImageFont.truetype("arial.ttf", cell_font_size)
        except:
            self.heading_font = ImageFont.load_default()
            self.cell_font = ImageFont.load_default()
    
    def get_text_size(self, text, font):
        dummy_img = Image.new("RGB", (1,1))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0,0), str(text), font=font)
        return bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    def render(self, save_path="table.png"):
        df = self.df
        n_rows, n_cols = df.shape
        
        # Column widths
        col_widths = []
        for col in df.columns:
            max_width = self.get_text_size(col, self.cell_font)[0]
            for val in df[col]:
                w = self.get_text_size(val, self.cell_font)[0]
                if w > max_width:
                    max_width = w
            col_widths.append(max_width + 2*self.cell_padding)
        
        header_height = self.get_text_size("Ag", self.cell_font)[1] + 2*self.cell_padding
        row_height = self.get_text_size("Ag", self.cell_font)[1] + 2*self.cell_padding
        heading_height = 0
        if self.heading:
            heading_height = self.get_text_size(self.heading, self.heading_font)[1] + 2*self.cell_padding
        
        img_width = sum(col_widths) + 1
        img_height = heading_height + header_height + n_rows*row_height + 1
        
        img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(img)
        
        # Draw heading
        y_offset = 0
        if self.heading:
            w, h = self.get_text_size(self.heading, self.heading_font)
            draw.text(((img_width - w)/2, (heading_height - h)/2),
                      self.heading, fill="black", font=self.heading_font)
            y_offset += heading_height
        
        # Draw header
        x = 0
        for i, col in enumerate(df.columns):
            w = col_widths[i]
            bg_color = self.header_row_bg
            fg_color = self.header_fg
            if i in self.column_bg:
                bg_color = self.column_bg[i]
            if i in self.column_fg:
                fg_color = self.column_fg[i]
            draw.rectangle([x, y_offset, x+w, y_offset+header_height], fill=bg_color, outline=self.border_color)
            tw, th = self.get_text_size(col, self.cell_font)
            draw.text((x + (w-tw)/2, y_offset + (header_height-th)/2), str(col), fill=fg_color, font=self.cell_font)
            x += w
        y_offset += header_height
        
        # Draw data rows
        for row_idx in range(n_rows):
            x = 0
            for col_idx in range(n_cols):
                w = col_widths[col_idx]
                
                # Background color priority: row > column > default
                bg_color = self.row_bg
                if row_idx in self.row_bg_dict:
                    bg_color = self.row_bg_dict[row_idx]
                if col_idx in self.column_bg:
                    bg_color = self.column_bg[col_idx]
                
                # Foreground color priority: cell > row > column > default black
                fg_color = "black"
                if col_idx in self.column_fg:
                    fg_color = self.column_fg[col_idx]
                if row_idx in self.row_fg_dict:
                    fg_color = self.row_fg_dict[row_idx]
                if (row_idx, col_idx) in self.cell_fg:
                    fg_color = self.cell_fg[(row_idx, col_idx)]
                
                draw.rectangle([x, y_offset, x+w, y_offset+row_height], fill=bg_color, outline=self.border_color)
                
                val = df.iloc[row_idx, col_idx]
                tw, th = self.get_text_size(val, self.cell_font)
                draw.text((x + (w-tw)/2, y_offset + (row_height-th)/2), str(val), fill=fg_color, font=self.cell_font)
                x += w
            y_offset += row_height
        
        img.save(save_path)
        print(f"Table image saved as {save_path}")


# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [25, 30, 35, 40],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
    }
    df = pd.DataFrame(data)

    # Highlight column, row, and cell foreground colors
    table_img = TableImage(
        df,
        heading="Employee Information",
        heading_font_size=48,
        column_bg={1: "#ffcccc"},   # Age column bg
        row_bg_dict={2: "#ccffcc"}, # 3rd row bg
        column_fg={2: "blue"},      # City column text color
        row_fg_dict={1: "green"},   # 2nd row text color
        cell_fg={(3,1): "red"},     # 4th row, Age cell text color
        header_row_bg="#ccccff",
        header_fg="darkred"
    )
    table_img.render("table_with_fg_bg.png")