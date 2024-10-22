from reportlab.platypus import Table

from config import IS_ARABIC, HALF_HEADER, SINGLE_COLUMN, HEADER_TABLE_RATIOS_DOUBLE, HEADER_TABLE_RATIOS_SINGLE
from styles_helpers import generate_root_table_style
from utils import ar, get_cols_from_ratios


def generate_columns_header():
    if SINGLE_COLUMN:
        return [ar(text) if IS_ARABIC else text for text in HALF_HEADER]
    else:
        return ([ar(text) if IS_ARABIC else text for text in HALF_HEADER + ["", ""]] * 2)[:-2]


def generate_root_header(root, font, page_width):
    if IS_ARABIC:
        header_data = [
            "",
            ar(root),
            "",
        ]
    else:
        header_data = [
            "",
            ar(root),
            "",
        ]
    header_row_cols = get_cols_from_ratios(
        HEADER_TABLE_RATIOS_SINGLE if SINGLE_COLUMN else HEADER_TABLE_RATIOS_DOUBLE,
        page_width * .9)

    table = Table([header_data], colWidths=header_row_cols)

    table.setStyle(generate_root_table_style(font))
    return table
