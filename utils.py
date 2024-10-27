# utils.py

import glob
import logging
import os
from collections import defaultdict

import pandas as pd
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display
from fuzzywuzzy import process
from fuzzywuzzy.fuzz import partial_ratio
from pyarabic.normalize import normalize_searchtext
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph

from config import DATA_REPEAT_MULTIPLIER, INPUT_DATA, SINGLE_COLUMN
from config import IS_ARABIC
from quran_data import load_quran_meta

reshaper = ArabicReshaper(configuration={
    'delete_harakat': True,
    'shift_harakat_position': False,
    'use_unshaped_instead_of_isolated': False,
    "support_zwj": False
})


def ar(text):
    reshaped_text = reshaper.reshape(text)
    return get_display(reshaped_text)


def get_numerals(number_string):
    if number_string is not None:
        number_string += 1
    else:
        number_string = ""
    number_string = str(number_string)

    if IS_ARABIC:
        arabic_numerals = {
            '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
            '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
        }
        return ''.join(arabic_numerals.get(digit, digit) for digit in number_string)

    return number_string


def load_source_data(path):
    df = pd.read_excel(path)
    records = df.to_dict(orient='records')
    meta = load_quran_meta()
    sura_name_ar = {int(sura["@index"]) - 1: sura["@name"] for sura in meta["quran"]["suras"]["sura"]}
    sura_name_en = {int(sura["@index"]) - 1: sura["@ename"] for sura in meta["quran"]["suras"]["sura"]}
    for entry in records:
        entry["aya_no"] = entry["aya_no"] - 1
        entry["sura_no"] = entry["sura_no"] - 1
        entry["sura_name_ar"] = sura_name_ar[entry["sura_no"]]
        entry["sura_name_en"] = sura_name_en[entry["sura_no"]]

    root_groups = defaultdict(list)
    for record in records:
        root_groups[record["root"]].append(record)
    for root_group in root_groups:
        root_groups[root_group].sort(key=lambda x: (x["sura_no"], x["aya_no"]))
        root_groups[root_group] *= DATA_REPEAT_MULTIPLIER
        if not SINGLE_COLUMN and len(root_groups[root_group]) % 2 == 1:
            default_entry = defaultdict(lambda: None)
            default_entry["sura_name_ar"] = default_entry["sura_name_en"] = default_entry["word"] = default_entry["word_en"] = ""
            root_groups[root_group].append(default_entry)

    return [(k, root_groups[k]) for k in sorted(root_groups)]


def find_token_index(meta_data, target_word):
    if len(target_word) == 0:
        return None

    # Perform fuzzy matching on the word list using the search key
    options = meta_data["simple"]
    word, score = process.extractOne(target_word, options, scorer=partial_ratio, processor=normalize_searchtext)

    found_idx = options.index(word)
    assert score > 70
    if score < 85:
        print("Fuzzy matching warning:", word, target_word, score)
    return found_idx


def canonicalize_entered_words(source_data, q_mapper):
    for root, entries in source_data:
        for entry in entries:
            sura, aya = entry["sura_no"], entry["aya_no"]
            quran_meta = q_mapper[sura, aya]
            idx = find_token_index(quran_meta, entry["word"])
            entry["word_font_id"] = quran_meta["font_id"]
            entry["ar_word_id"] = idx
            entry["word_font_symbol"] = None if idx is None else quran_meta["symbols"][idx]
            entry["simple_equivalent"] = None if idx is None else quran_meta["simple"][idx]
            entry["uthmani_equivalent"] = None if idx is None else quran_meta["uthmani"][idx]
    extended_data_path = INPUT_DATA.replace(".xlsx", "-extended.xlsx")
    pd.DataFrame(sum([a for _, a in source_data], []), ).to_excel(extended_data_path)
    logging.info(f"{extended_data_path} has been saved..")
    return source_data


def is_non_decreasing(lst):
    for i in range(len(lst) - 1):
        if lst[i] > lst[i + 1]:
            return False
    return True


class ArParagraph(Paragraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def breakLines(self, width):
        broken = super().breakLines(width)
        ara_lines = []
        for line_data in broken.lines:
            if isinstance(line_data, tuple):
                rem, lines = line_data
                ara_lines.append((rem, [line[::-1] for line in lines]))
            else:
                for word in line_data.words:
                    word.text = word.text[::-1]
                line_data.words = line_data.words[::-1]
                ara_lines.append(line_data)

        broken.lines = ara_lines

        return broken


def register_fonts():
    ttf_files = sorted(glob.glob(os.path.join("fonts", "*.ttf")))
    for ttf_file in ttf_files:
        font_name = os.path.splitext(os.path.basename(ttf_file))[0]
        pdfmetrics.registerFont(TTFont(font_name, ttf_file))

    specific_fonts = [
        ("Nabi", "Nabi Regular.ttf"),
        ("me_quran", "me_quran Regular.ttf"),
        ("Arial", "Arial-Unicode-Bold.ttf"),
    ]
    for font_name, font_file in specific_fonts:
        pdfmetrics.registerFont(TTFont(font_name, f"resources/fonts/{font_file}"))

    noto_fonts = ["Bold", "Medium", "Regular", "SemiBold", "VariableFont_wght"]
    for noto_font in noto_fonts:
        font_name = f"NotoNaskhArabic-{noto_font}"
        pdfmetrics.registerFont(TTFont(font_name, f"resources/fonts/{font_name}.ttf"))


def get_cols_from_ratios(ratios, page_width):
    total = sum(ratios)
    ratios = [ratio / total for ratio in ratios]
    return [page_width * ratio for ratio in ratios]


def get_sura_name_cells(entry, eng_style, ar_style):
    if IS_ARABIC:
        return Paragraph(ar(entry["sura_name_ar"]), ar_style)
    return [
        Paragraph(ar(entry["sura_name_en"]), eng_style),
        Paragraph(ar(entry["sura_name_ar"]), ar_style),
    ]
