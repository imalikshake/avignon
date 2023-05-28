import cv2
import pandas as pd

def put_text_wrap(img, text, org, font, font_scale, color, thickness, line_spacing, max_width):
    words = text.split()  # Split text into individual words
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the current word exceeds the maximum width
        if cv2.getTextSize(current_line + " " + word, font, font_scale, thickness)[0][0] <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line.strip())
            current_line = word

    lines.append(current_line.strip())  # Add the last line

    # Draw each line of text with appropriate y-coordinates
    for i, line in enumerate(lines):
        y = org[1] + (i * line_spacing)
        cv2.putText(img, line, (org[0], y), font, font_scale, color, thickness)

def translate_data(csv_path, sep="|"):
    data_df = df = pd.read_csv(csv_path, sep=sep,)
    ratios = []
    for number in data_df["numbers"]:
        if '%' in number:
            value = number.replace("%", "")
            ratio = float(value)/100
        elif 'jours' in number:
            ratio = 1.0
        else:
            value = int(number)
            length = len(str(value))
            max_length = int('9' * length)
            ratio = value/max_length
        ratios.append(ratio)
    data_df["ratio"] = ratios
    return data_df

def get_coords(digit, rows, cols):
    position = digit % (rows*cols) 
    row = position // cols 
    col = position % cols 
    return row, col
