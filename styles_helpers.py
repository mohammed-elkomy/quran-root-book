# pdf_generation.py
import glob
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import TableStyle

from config import GENERAL_ARABIC_FONT, QURAN_FONT_SIZE, QURAN_LINE_SPACING, GENERAL_ENGLISH_FONT, GENERAL_FONT_SIZE, TRANSLATION_LINE_SPACING, HEADER_PADDING, TABLE_PADDING, TABLE_BK_COLOR, QURAN_ROW_SEPARATOR, ROOT_HEADER_BK_COLOR, ROOT_BG_COLOR, ROOT_BORDER_COLOR
from config import IS_ARABIC


def get_root_subtable_style():
    return [
        ('VALIGN', (0, 0), (-1, 0), 'BOTTOM'),
        ('VALIGN', (0, 1), (-1, 1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), -2),

        ('TOPPADDING', (0, 1), (-1, 1), 2 if IS_ARABIC else -2),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 2 if IS_ARABIC else 1),
        ('TOPPADDING', (0, 0), (-1, 0), -10 if IS_ARABIC else 1),

        ('BACKGROUND', (1, 0), (1, -1), ROOT_BG_COLOR),
        ('BOX', (1, 0), (1, -1), 1, ROOT_BORDER_COLOR)
    ]


def generate_root_table_style(font):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ROOT_HEADER_BK_COLOR),
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('FONTSIZE', (0, 0), (-1, -1), GENERAL_FONT_SIZE * 1.2),
        ('ALIGN', (0, 0), (0, -1), "LEFT"),
        ('ALIGN', (1, 0), (1, -1), "CENTER"),
        ('ALIGN', (2, 0), (2, -1), "RIGHT"),
        # ('RIGHTPADDING', (-1, 0), (-1, -1), 10),
        # ('LEFTPADDING', (0, 0), (0, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), TABLE_PADDING / 2),
        ('TOPPADDING', (0, 0), (-1, -1), TABLE_PADDING * 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.darkred),
    ])


def generate_style_per_entry(fill_data, ):
    general_font = GENERAL_ARABIC_FONT if IS_ARABIC else GENERAL_ENGLISH_FONT
    tbl_style = get_generic_table_style()
    table_style = TableStyle(tbl_style)
    for font_row_idx, row in enumerate(fill_data):
        if font_row_idx < 2:
            table_style.add('BACKGROUND', (0, font_row_idx), (-1, font_row_idx), TABLE_BK_COLOR)
            table_style.add('FONTNAME', (0, font_row_idx), (-1, font_row_idx), general_font)
            table_style.add('FONTSIZE', (0, font_row_idx), (-1, font_row_idx), GENERAL_FONT_SIZE)
            # table_style.add('FONTSIZE', (0, font_row_idx), (-1, font_row_idx), GENERAL_FONT_SIZE)
        else:
            for col_idx, _ in enumerate(row):
                table_style.add('BACKGROUND', (col_idx, font_row_idx), (col_idx, font_row_idx), TABLE_BK_COLOR)
                table_style.add('LINEABOVE', (col_idx, font_row_idx), (col_idx, font_row_idx), 0.05, colors.black if QURAN_ROW_SEPARATOR else colors.transparent)
                # table_style.add('LINEABOVE', (col_idx, font_row_idx), (col_idx, font_row_idx), 0.0, colors.transparent)
                table_style.add('SPAN', (3, font_row_idx), (4, font_row_idx)) # todo single column
                table_style.add('SPAN', (10, font_row_idx), (11, font_row_idx))
                table_style.add('ALIGN', (0, font_row_idx), (-1, font_row_idx), 'CENTER')
    return table_style


def generate_quranic_paragraph_styles():
    quran_style = {}
    for ttf_file in glob.glob(os.path.join("fonts", "p[0-9]*.ttf")):
        font_name = os.path.splitext(os.path.basename(ttf_file))[0]
        full_aya_style = ParagraphStyle(font_name,
                                        fontName=font_name,
                                        fontSize=QURAN_FONT_SIZE * 1.25 if font_name in ["p1", "p2"] else QURAN_FONT_SIZE,
                                        alignment=TA_RIGHT,
                                        leading=QURAN_LINE_SPACING, allowWidows=False, )
        root_style = ParagraphStyle(font_name + "-root",
                                    fontName=font_name,
                                    fontSize=QURAN_FONT_SIZE * 1.25 * 1.15 if font_name in ["p1", "p2"] else QURAN_FONT_SIZE * 1.15,
                                    textColor=colors.darkblue,  # Set the text color to dark blue
                                    alignment=TA_CENTER,
                                    leading=QURAN_LINE_SPACING, allowWidows=False, )
        quran_style[font_name] = full_aya_style, root_style
    return quran_style


def generate_styles():
    font_name = GENERAL_ARABIC_FONT if IS_ARABIC else GENERAL_ENGLISH_FONT

    # Define the shared styles for numerals and sura names
    numeral_style = ParagraphStyle(
        'numeral',
        fontName=font_name,
        fontSize=GENERAL_FONT_SIZE,
        alignment=TA_CENTER,
        splitLongWords=False,
    )

    centered_eng_style = ParagraphStyle(
        'centered_style_eng',
        fontName=GENERAL_ENGLISH_FONT,
        fontSize=GENERAL_FONT_SIZE,
        alignment=TA_CENTER,
        splitLongWords=False,
    )

    english_root_style = ParagraphStyle(
        'root_centered_style_eng',
        fontName=GENERAL_ENGLISH_FONT,
        fontSize=GENERAL_FONT_SIZE * 1.2,
        textColor=colors.darkblue,  # Set the text color to dark blue
        alignment=TA_CENTER,
        splitLongWords=False,
    )

    centered_ar_style = ParagraphStyle(
        'centered_style_ar',
        fontName=GENERAL_ARABIC_FONT,
        fontSize=GENERAL_FONT_SIZE,
        alignment=TA_CENTER,
        splitLongWords=False,
    )

    trans_style = ParagraphStyle(
        'left_aligned_style',
        fontName=GENERAL_ENGLISH_FONT,
        fontSize=GENERAL_FONT_SIZE,
        alignment=TA_LEFT,
        leading=TRANSLATION_LINE_SPACING,
        spaceBefore=TRANSLATION_LINE_SPACING,
        allowWidows=False,
    )

    return numeral_style, centered_eng_style, english_root_style, centered_ar_style, trans_style


def get_generic_table_style():
    return [
        # row 0
        ('SPAN', (0, 0), (-1, 0)),

        # row 1
        ('ALIGN', (0, 1), (-1, 1), "CENTER"),
        ('ALIGN', (3, 1), (4, 1), "RIGHT"),
        ('ALIGN', (10, 1), (11, 1), "RIGHT"),
        ('LINEABOVE', (0, 1), (-1, 1), 0.5, colors.black),
        ('LINEBELOW', (0, 1), (4, 1), 0.5, colors.black),
        ('LINEBELOW', (7, 1), (-1, 1), 0.5, colors.black),

        ('LINEAFTER', (5, 0), (5, -1), 1, colors.darkred), # todo single column
        ('LINEBEFORE', (6, 0), (6, -1), 1, colors.darkred),
        ('RIGHTPADDING', (4, 0), (4, -1), 1),
        ('LEFTPADDING', (7, 0), (7, -1), 1),
        ('RIGHTPADDING', (5, 0), (5, -1), 0),
        ('LEFTPADDING', (5, 0), (5, -1), 0),
        ('RIGHTPADDING', (6, 0), (6, -1), 0),
        ('LEFTPADDING', (6, 0), (6, -1), 0),
        ('LEFTPADDING', (0, 0), (0, -1), 1),
        ('RIGHTPADDING', (11, 0), (12, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, 1), HEADER_PADDING),
        ('BOTTOMPADDING', (0, 1), (-1, -1), TABLE_PADDING),
        ('TOPPADDING', (0, 0), (-1, -1), TABLE_PADDING),
        ('INNERGRID', (0, 2), (-1, -2), 0.5, colors.transparent),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]

def get_padding_table_style():
    return [("FONTSIZE", (0, 0), (-1, -1), 1)]

