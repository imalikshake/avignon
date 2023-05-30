import cv2
import pandas as pd


def put_text_wrap(img, text, org, font, font_scale, color, thickness, line_spacing, max_width):
    """
    Wrap text within a given width and draw it on an image.

    Parameters:
    - img: Image on which the text will be drawn.
    - text: Text to be wrapped and drawn.
    - org: Origin coordinates (x, y) for the text.
    - font: Font type for the text.
    - font_scale: Font scale factor.
    - color: Color of the text.
    - thickness: Thickness of the text.
    - line_spacing: Spacing between lines of text.
    - max_width: Maximum width for each line of text.

    Returns:
    - None
    """

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


def get_coords(digit, rows, cols):
    """
    Calculate the row and column coordinates for a given digit in a grid.

    Parameters:
    - digit: Digit number.
    - rows: Number of rows in the grid.
    - cols: Number of columns in the grid.

    Returns:
    - Row and column coordinates as a tuple.
    """

    position = digit % (rows * cols)
    row = position // cols
    col = position % cols
    return row, col

