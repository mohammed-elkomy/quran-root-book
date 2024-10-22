from reportlab.lib import colors

#######################################
# input and output
INPUT_DATA = "resources/data.xlsx"
OUTPUT_PDF = "generated_output.pdf"
# options for generated file
PDF_TITLE = "Sample PDF Title"
PDF_AUTHOR = "Your Name"
PDF_SUBJECT = "PDF Subject"
PDF_KEYWORDS = "PDF, ReportLab, Metadata"
PDF_CREATOR = "Your Application Name"
#######################################
# resource files
MUSHAF_RES = "resources/mushaf.txt"
MUSHAF_META = "resources/quran-data.xml"
QURAN_TEXT = "resources/quran-uthmani.xml"
UTH_TO_SIMPLE = "resources/Uthmani to Simple Mapping.html"
TRANSLATION_XML = "resources/english_translation.xml"
#######################################
# fonts options
GENERAL_ARABIC_FONT = "NotoNaskhArabic-SemiBold"
GENERAL_ENGLISH_FONT = "Arial"
"""
SELECT A FONT:
me_quran
Arial
NotoNaskhArabic-Bold
NotoNaskhArabic-Medium
NotoNaskhArabic-Regular
NotoNaskhArabic-SemiBold
NotoNaskhArabic-VariableFont_wght
"""

QURAN_FONT_SIZE = 8
###################################
# color options
ROOT_HEADER_BK_COLOR = colors.beige
TABLE_BK_COLOR = colors.white
ROOT_BORDER_COLOR = colors.Color(red=0, green=0, blue=0)
ROOT_BG_COLOR = colors.Color(red=0.8, green=0.2, blue=0.0, alpha=0.1)
###################################
# layout options
IS_ARABIC = False  # Globalisation

TABLE_PADDING = 3
QURAN_LINE_SPACING = 13

HEADER_PADDING_AR = 3  # 3 for arabic and 0 for english
HEADER_PADDING_EN = 0  # 3 for arabic and 0 for english
GENERAL_ARABIC_FONT_SIZE_AR = 7  # 7 for arabic and 5.5 for english
GENERAL_ARABIC_FONT_SIZE_EN = 5.5  # 7 for arabic and 5.5 for english
HEADER_NAMES_AR = ["رقمها", "السورة", "رقمها", "الآية", "", ]
HEADER_NAMES_EN = ["Sura No", "Sura", "Aya No", "Verse", "", ]

QURAN_ROW_SEPARATOR = False
TRANSLATION_LINE_SPACING = 10
###################################
GENERAL_TABLE_RATIOS = [1.25, 2.5, 1.25, 7, 3,
                        .2, .2,
                        1.25, 2.5, 1.25, 7, 3]  # width ratios

if IS_ARABIC:
    HALF_HEADER = HEADER_NAMES_AR
    HEADER_PADDING = HEADER_PADDING_AR
    GENERAL_FONT_SIZE = GENERAL_ARABIC_FONT_SIZE_AR
else:
    HALF_HEADER = HEADER_NAMES_EN
    HEADER_PADDING = HEADER_PADDING_EN
    GENERAL_FONT_SIZE = GENERAL_ARABIC_FONT_SIZE_EN

###################################
# FOR TESTING
DATA_REPEAT_MULTIPLIER = 1
