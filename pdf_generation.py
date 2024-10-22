# pdf_generation.py
import logging
import os
from collections import defaultdict
from copy import deepcopy
from functools import partial

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.platypus.doctemplate import _doNothing
from tqdm import tqdm

from bookmarks_helper import extract_root_tables_from_super_table, add_page_bookmarks
from config import GENERAL_ARABIC_FONT, GENERAL_TABLE_RATIOS, PDF_TITLE, PDF_AUTHOR, PDF_SUBJECT, PDF_KEYWORDS, PDF_CREATOR
from config import IS_ARABIC
from headers_helpers import generate_columns_header, generate_root_header
from quran_data import load_translation, create_font_text_mapping
from styles_helpers import generate_quranic_paragraph_styles, generate_styles, generate_style_per_entry, get_root_subtable_style, get_padding_table_style
from utils import ArParagraph, get_numerals, load_source_data, is_non_decreasing, canonicalize_entered_words, register_fonts, get_sura_name_cells, get_cols_from_ratios


def highlight_quran(meta_data, found_idx, highlight_color="red"):
    if found_idx is None:
        return ""
    symbol_sequence = "".join(meta_data["symbols"][:-1])
    highlighted_text = (
            symbol_sequence[:found_idx] +
            f'<font color="{highlight_color}">{symbol_sequence[found_idx]}</font>' +
            symbol_sequence[found_idx + 1:]
    )
    return highlighted_text


def get_root_representation(meta_data, found_idx, entry):
    if found_idx is None:
        return "", ""
    return meta_data["symbols"][found_idx], entry["word_en"]


def process_current_root(last_root, current_root, root_text):
    if last_root is None or last_root != root_text:
        return root_text, current_root
    else:
        return root_text, ""


def get_root_subtable(root_text, root_style, eng_word_style):
    if any(root_text):
        ara_text, eng_text = root_text
        eng_paragraph = []
        if not IS_ARABIC:
            eng_paragraph.extend([" ", Paragraph(eng_text, eng_word_style), " "])

        root_table = Table([eng_paragraph, ["  ", ArParagraph(ara_text, root_style), " "]], )
        style_list = get_root_subtable_style()
        root_table.setStyle(style_list)
        padding_table = Table([[""]], )
        padding_table.setStyle(get_padding_table_style())
        return [root_table, padding_table]
    else:
        return []


def generate_content_tables(source_data, page_width, q_mapper):
    quranic_styles = generate_quranic_paragraph_styles()
    source_data = canonicalize_entered_words(source_data, q_mapper)
    trans_lookup = load_translation()

    centered_numeral_style, centered_text_eng_style, english_root_style, centered_text_ar_style, trans_style = generate_styles()

    tables = []
    last_root = None
    for root, entries in source_data:
        root_header = generate_root_header(root, GENERAL_ARABIC_FONT, page_width)
        fill_data = [[root_header]] + [generate_columns_header()]

        for idx in range(0, len(entries), 2): # todo single column
            entry_right, entry_left = entries[idx], entries[idx + 1]
            r_sura, l_sura = entry_right["sura_no"], entry_left["sura_no"]
            r_aya, l_aya = entry_right["aya_no"], entry_left["aya_no"]
            meta_right, meta_left = q_mapper[r_sura, r_aya], q_mapper[l_sura, l_aya]
            left_aya_style, left_root_style = quranic_styles[meta_left["font_id"]]
            right_aya_style, right_root_style = quranic_styles[meta_right["font_id"]]

            left_idx = entry_left["ar_word_id"]
            right_idx = entry_right["ar_word_id"]

            right_root = get_root_representation(meta_right, right_idx, entry_right)
            last_root, right_root = process_current_root(last_root, right_root, (entry_right["word"], entry_right["word_en"]))
            right_quranic_text = (get_root_subtable(right_root, right_root_style, english_root_style) +
                                  [ArParagraph(highlight_quran(meta_right, right_idx), right_aya_style)])

            left_root = get_root_representation(meta_left, left_idx, entry_left)
            last_root, left_root = process_current_root(last_root, left_root, (entry_left["word"], entry_left["word_en"]))
            left_quranic_text = (get_root_subtable(left_root, left_root_style, english_root_style)
                                 + [ArParagraph(highlight_quran(meta_left, left_idx), left_aya_style), ])

            if not IS_ARABIC:
                left_quranic_text = left_quranic_text + [Paragraph(trans_lookup[l_sura, l_aya], trans_style)]

                right_quranic_text = right_quranic_text + [Paragraph(trans_lookup[r_sura, r_aya], trans_style)]

            #                 left_quranic_text = Paragraph(ar(
            #                     """
            # يَـٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُوٓا۟ إِذَا تَدَايَنتُم بِدَيْنٍ إِلَىٰٓ أَجَلٍۢ مُّسَمًّۭى فَٱكْتُبُوهُ ۚ وَلْيَكْتُب بَّيْنَكُمْ كَاتِبٌۢ بِٱلْعَدْلِ ۚ وَلَا يَأْبَ كَاتِبٌ أَن يَكْتُبَ كَمَا عَلَّمَهُ ٱللَّهُ ۚ فَلْيَكْتُبْ وَلْيُمْلِلِ ٱلَّذِى عَلَيْهِ ٱلْحَقُّ وَلْيَتَّقِ ٱللَّهَ رَبَّهُۥ وَلَا يَبْخَسْ مِنْهُ شَيْـًۭٔا ۚ فَإِن كَانَ ٱلَّذِى عَلَيْهِ ٱلْحَقُّ سَفِيهًا أَوْ ضَعِيفًا أَوْ لَا يَسْتَطِيعُ أَن يُمِلَّ هُوَ فَلْيُمْلِلْ وَلِيُّهُۥ بِٱلْعَدْلِ ۚ وَٱسْتَشْهِدُوا۟ شَهِيدَيْنِ مِن رِّجَالِكُمْ ۖ فَإِن لَّمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌۭ وَٱمْرَأَتَانِ مِمَّن تَرْضَوْنَ مِنَ ٱلشُّهَدَآءِ أَن تَضِلَّ إِحْدَىٰهُمَا فَتُذَكِّرَ إِحْدَىٰهُمَا ٱلْأُخْرَىٰ ۚ وَلَا يَأْبَ ٱلشُّهَدَآءُ إِذَا مَا دُعُوا۟ ۚ وَلَا تَسْـَٔمُوٓا۟ أَن تَكْتُبُوهُ صَغِيرًا أَوْ كَبِيرًا إِلَىٰٓ أَجَلِهِۦ ۚ ذَٰلِكُمْ أَقْسَطُ عِندَ ٱللَّهِ وَأَقْوَمُ لِلشَّهَـٰدَةِ وَأَدْنَىٰٓ أَلَّا تَرْتَابُوٓا۟ ۖ إِلَّآ أَن تَكُونَ تِجَـٰرَةً حَاضِرَةًۭ تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا ۗ وَأَشْهِدُوٓا۟ إِذَا تَبَايَعْتُمْ ۚ وَلَا يُضَآرَّ كَاتِبٌۭ وَلَا شَهِيدٌۭ ۚ وَإِن تَفْعَلُوا۟ فَإِنَّهُۥ فُسُوقٌۢ بِكُمْ ۗ وَٱتَّقُوا۟ ٱللَّهَ ۖ وَيُعَلِّمُكُمُ ٱللَّهُ ۗ وَٱللَّهُ بِكُلِّ شَىْءٍ عَلِيمٌۭ
            #                                     """), centered_text_ar_style
            #                 )
            fill_data.append([
                # left sura num
                Paragraph(get_numerals(l_sura), centered_numeral_style),
                # left sura name
                get_sura_name_cells(entry_left, centered_text_eng_style, centered_text_ar_style),
                # left aya num
                Paragraph(get_numerals(l_aya), centered_numeral_style),
                # left quranic text
                left_quranic_text,
                # padding
                "",
                "",
                "",
                # right sura num
                Paragraph(get_numerals(r_sura), centered_numeral_style),
                # right sura name
                get_sura_name_cells(entry_right, centered_text_eng_style, centered_text_ar_style),
                # right aya num
                Paragraph(get_numerals(r_aya), centered_numeral_style),
                # right quranic text
                right_quranic_text,
                # padding
                ""
            ])

        main_table_cols = get_cols_from_ratios(GENERAL_TABLE_RATIOS, page_width * .9)
        table = Table(fill_data, colWidths=main_table_cols, repeatRows=2, )

        table_style = generate_style_per_entry(fill_data)

        table.setStyle(table_style)
        tables.append(table)
    return tables


class QuranDocument(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        # bookmark tracking
        self.entries_per_table = None
        self.page_id = 1
        self.current_root_idx = -1
        self.bookmarks = []

        # progress tracking
        self.total_flowables = 0
        self.processed_flowables = 0
        # Initialize the tqdm progress bar
        self.pbar = None
        self.total_entries = 0
        # rendered rows tracking
        self.rendered_counts = []
        self.roots_per_page = defaultdict(list)

    def afterPage(self):
        if self.is_last and self.bookmarks[-1][0] == self.page_id:
            # fix bookmark of last entry
            self.bookmarks[-1][0] += 1
        self.page_id += 1

    def afterFlowable(self, flowable):
        self.is_last = False
        self.processed_flowables += 1

        if self.entries_per_table and isinstance(flowable, Table):
            self.roots_per_page[self.page_id].extend(extract_root_tables_from_super_table(flowable))
            last_rendered = len(flowable._cellvalues) - 2
            current_root = self.entries_per_table[self.current_root_idx]
            current_root[1] -= last_rendered

            assert current_root[1] >= 0, current_root
            if current_root[1] == 0 and self.current_root_idx < len(self.entries_per_table) - 1:
                self.push_bookmark()
                self.is_last = True

            self.rendered_counts.append(last_rendered)
            self.pbar.update(last_rendered)

    def push_bookmark(self):
        if self.entries_per_table:
            self.current_root_idx += 1
            if self.current_root_idx < len(self.entries_per_table):
                root = self.entries_per_table[self.current_root_idx][0]
                self.bookmarks.append([self.page_id, root])

    def build(self, flowables, onFirstPage=_doNothing, onLaterPages=_doNothing, canvasmaker=canvas.Canvas, entries_per_table=None):
        self.entries_per_table = deepcopy(entries_per_table)
        self.total_entries = sum([e for _, e in self.entries_per_table])
        self.push_bookmark()
        self.pbar = tqdm(total=self.total_entries, desc="Building PDF", unit="Entries")

        self.total_flowables = len(flowables)
        super().build(deepcopy(flowables), onFirstPage, onLaterPages, canvasmaker)

    def get_bookmarks_lookup(self, source_data):
        """Creates a comprehensive mapping of Quranic text to font symbols and returns a lookup dictionary."""
        if IS_ARABIC:
            bookmarks = self.get_extended_arabic_nested_bookmarks(source_data)
        else:
            bookmarks = defaultdict(list)
            for page, pairs in self.roots_per_page.items():
                bookmarks[page] = [[pair[1][0], pair[1]] for pair in pairs]

            first_occ = defaultdict(lambda: 1e100)
            for page, entries in bookmarks.items():
                for entry in entries:
                    first_char = entry[0]
                    first_occ[first_char] = min(first_occ[first_char], page)
            for first_char, first_page in first_occ.items():
                bookmarks[first_page] = [[first_char]] + bookmarks[first_page]
            bookmarks[1] = [None] + bookmarks[1]

        return bookmarks

    def get_extended_arabic_nested_bookmarks(self, source_data):
        symbol_to_root_path = {}
        for root, tokens in source_data:
            for token in tokens:
                symbol_to_root_path[(token["word_font_id"], token["word_font_symbol"])] = root.split() + [token["simple_equivalent"]]
        assert is_non_decreasing([p for p, _ in self.bookmarks]), [p for p, _ in self.bookmarks]
        first_occ = defaultdict(lambda: 1e100)
        for page, root in self.bookmarks:
            for idx in range(1, len(root) + 1):
                subroot = root[:idx].strip()
                first_occ[subroot] = min(first_occ[subroot], page)
        nested_bookmarks = defaultdict(list)
        for subroot, page in first_occ.items():
            nested_bookmarks[page].append(subroot.split())
        nested_bookmarks[1] = [None] + nested_bookmarks[1]
        linear_bookmarks = self.roots_per_page
        for page, pairs in linear_bookmarks.items():
            linear_bookmarks[page] = [symbol_to_root_path[pair] for pair in pairs]  # if the font,text pair is not found return the word as is (for non arabic version)
        all_pages = sorted(set(nested_bookmarks.keys()).union(linear_bookmarks.keys()))
        extended_bookmarks = defaultdict(list)
        for k in all_pages:
            extended = sorted(nested_bookmarks[k] + linear_bookmarks[k], key=lambda item: "-".join(item) if item else "")
            extended_bookmarks[k] = extended
        return extended_bookmarks

    def distribute_entries(self, source_data):
        assert sum(self.rendered_counts) == self.total_entries
        current = 0
        distributed_data = []
        for count in self.rendered_counts:
            current_root, current_entries = source_data[current]
            distributed_data.append((current_root, current_entries[:count * 2])) # todo single column
            current_entries[:] = current_entries[count * 2:]
            if len(current_entries) == 0:
                current += 1
        return distributed_data


def generate_pdf(source_path, output_path):
    source_data = load_source_data(source_path)
    entries_per_table = [[root, len(entries) // 2] for root, entries in source_data] # todo single column
    register_fonts()
    p_width, p_height = A4
    pdf = QuranDocument("tmp.pdf", pagesize=(p_width, p_height), bottomMargin=.05 * p_height, topMargin=.05 * p_height)

    q_mapper = create_font_text_mapping()
    content_tables = generate_content_tables(source_data, p_width, q_mapper)
    logging.info("Performing layout calculations")
    pdf.build(content_tables, entries_per_table=entries_per_table, )
    bookmarks_lookup = pdf.get_bookmarks_lookup(source_data)
    # distributed_data = pdf.distribute_entries(source_data)
    # generate_content_tables(distributed_data, p_width,)
    pdf = QuranDocument(output_path, pagesize=(p_width, p_height), bottomMargin=.05 * p_height, topMargin=.05 * p_height)
    os.remove("tmp.pdf")

    logging.info("Rendering layout..")

    # Set the document metadata
    pdf.title = PDF_TITLE
    pdf.author = PDF_AUTHOR
    pdf.subject = PDF_SUBJECT
    pdf.keywords = PDF_KEYWORDS
    pdf.creator = PDF_CREATOR

    pdf.build(
        content_tables, entries_per_table=entries_per_table,
        onFirstPage=partial(add_page_bookmarks, bookmarks_lookup=bookmarks_lookup, ),
        onLaterPages=partial(add_page_bookmarks, bookmarks_lookup=bookmarks_lookup),
    )
