import json
import re
from collections import defaultdict

import xmltodict

from config import MUSHAF_RES, MUSHAF_META, QURAN_TEXT, TRANSLATION_XML, UTH_TO_SIMPLE


def load_ayas_fonts_per_page():
    """Loads font data for each page of the Quran."""
    ayas_font = []
    with open(MUSHAF_RES, 'r') as f:
        for line in f:
            page_id, chars = line.strip().split(',', 1)
            # Fix incorrect repeated characters in certain cases
            if chars == "ﭧﭨﭩﭪﭫﭬﭭﭮﭯﭰﭱﭲﭳﭴﭵﭶﭷﭸﭹﭺﭻﭼﭽﭾﭾﭿﮀ":
                chars = "".join(sorted(set(chars)))
                # Remove repetition
                # فَوَيْلٌۭ لِّلَّذِينَ يَكْتُبُونَ ٱلْكِتَـٰبَ بِأَيْدِيهِمْ ثُمَّ يَقُولُونَ هَـٰذَا مِنْ عِندِ ٱللَّهِ لِيَشْتَرُوا۟ بِهِۦ ثَمَنًۭا قَلِيلًۭا ۖ فَوَيْلٌۭ لَّهُم مِّمَّا كَتَبَتْ أَيْدِيهِمْ وَوَيْلٌۭ لَّهُم مِّمَّا يَكْسِبُونَ ٧٩

            ayas_font.append({"font_id": f"p{page_id}", "symbols": chars})
    return ayas_font


def load_quran_meta():
    """Loads Quran metadata from an XML file."""
    with open(MUSHAF_META, 'r') as f:
        meta_quran = xmltodict.parse(f.read())
    return meta_quran


def load_quran_text():
    """Loads Quran text from an XML file."""
    with open(QURAN_TEXT, 'r') as f:
        quran_text = xmltodict.parse(f.read())
    return quran_text


def generate_aligned_pairs():
    """Aligns Quranic text with font symbols, ensuring proper mapping for each aya."""
    ayas_font = load_ayas_fonts_per_page()
    suras_meta = load_quran_meta()["quran"]["suras"]["sura"]
    quran_sura_text = load_quran_text()["quran"]["sura"]

    quran_text_to_font_pairs = []

    for sura in suras_meta:
        aya_idx = int(sura["@start"])  # Start index of the sura's ayas
        aya_count = int(sura["@ayas"])  # Number of ayas in this sura
        sura_id = int(sura["@index"]) - 1  # Sura index (0-based)
        sura_text = quran_sura_text[sura_id]["aya"]

        # Ensure the sura has the correct number of ayas
        assert len(sura_text) == aya_count

        for aya_id, aya_font in enumerate(ayas_font[aya_idx:aya_idx + aya_count]):
            # Split the aya text into tokens (words)
            aya_tokens = sura_text[aya_id]["@text"].split()
            # Get the corresponding font symbols for the aya
            aya_symbol_mapping = list(aya_font["symbols"])

            # Handle manual misalignment fixes for specific sura/aya pairs
            if (sura_id, aya_id) == (68, 7):
                aya_symbol_mapping = aya_symbol_mapping[:-1]  # Remove extra empty symbol
            if (sura_id, aya_id) == (12, 36):
                aya_tokens = aya_tokens[:8] + ["".join(aya_tokens[8:10])] + aya_tokens[10:]  # Merge tokens بَعْدَمَا insted of بَعْدَ مَا

            # Ensure there's alignment between tokens and symbols
            assert len(aya_tokens) == len(aya_symbol_mapping) - 1

            # Add the aligned data to the final mapping list
            quran_text_to_font_pairs.append({
                "sura_no": sura_id + 1,
                "aya_no": aya_id + 1,
                "font_id": aya_font["font_id"],
                "uthmani_tokens": aya_tokens,
                "font_symbols": aya_symbol_mapping
            })

    assert len(quran_text_to_font_pairs) == 6236  # Ensure all 6236 ayas are processed
    return quran_text_to_font_pairs


def create_font_text_mapping():
    """Creates a comprehensive mapping of Quranic text to font symbols and returns a lookup dictionary."""

    # Align text and font data for all suras and ayas
    aligned_pairs = generate_aligned_pairs()
    uth_to_simple = dict(load_uthmani_to_simple_pairs())

    # Create a lookup dictionary from the generated pairs
    lookup = defaultdict(lambda: {"symbols": "", "font_id": "p1"})
    uthm_token_lookup = {}
    for entry in aligned_pairs:
        key = (entry["sura_no"] - 1, entry["aya_no"] - 1)
        lookup[key] = {"symbols": entry["font_symbols"],
                       "uthmani": entry["uthmani_tokens"],
                       "font_id": entry["font_id"],
                       "simple": [uth_to_simple[w] for w in entry["uthmani_tokens"]]
                       }
        for symbol, uthmani_token in zip(entry["font_symbols"], lookup[key]["uthmani"]):
            uthm_token_lookup[entry["font_id"], symbol] = uthmani_token
    return lookup


def replace_repeated_hyphens(text):
    """Removes sequences of hyphens longer than 10 from the text."""
    pattern = r'-{11,}'  # Matches sequences of 11 or more hyphens
    return re.sub(pattern, "", text)


def load_translation():
    """Reads a Quran translation file and removes repeated hyphens from the text."""
    lookup = defaultdict(lambda: "")  # Default to empty string if not found
    with open(TRANSLATION_XML, 'r') as f:
        quran_trans = xmltodict.parse(replace_repeated_hyphens(f.read()))
        for sura in quran_trans["quran"]["sura"]:
            sura_id = int(sura["@index"]) - 1
            for aya in sura["aya"]:
                aya_index = int(aya["@index"]) - 1
                lookup[sura_id, aya_index] = aya["@text"]
    return lookup


def load_uthmani_to_simple_pairs():
    """
    Parses an HTML table with Arabic text into a list of tuples.

    Each tuple contains two Arabic text entries, extracted from <td> tags.

    Returns:
        List[Tuple[str, str]]: A list of tuples with Arabic text.
    """
    uth_to_simple_pairs = []

    # Regex to capture Arabic text within <td> tags
    td_pattern = re.compile(r'<td>(.*?)</td>')

    with open(UTH_TO_SIMPLE, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        for line in lines:
            # Find all text inside <td> tags in a line
            matches = td_pattern.findall(line)
            if len(matches) == 2:  # We expect 2 <td> values per row
                uth_to_simple_pairs.append((matches[0], matches[1]))
    # those uthmani tokens were not found in the original collection from https://qurananalysis.com/analysis/uthmani-to-simple.php?lang=en
    manual_tanzil_uth_to_ref_uth = [
        ('إِبْرَٰهِـۧمَ', 'إِبْرَٰهِۦمَ'),
        ('إِبْرَٰهِـۧمُ', 'إِبْرَٰهِۦمُ'),
        ('بَعْدَمَا', 'بَعْدَمَا'),
        ('بِٱلنَّبِيِّـۧنَ', 'بِٱلنَّبِيِّۦنَ'),
        ('بِٱلْـَٔاخِرَةِ', 'بِٱلْءَاخِرَةِ'),
        ('بِٱلْـَٔايَٰتِ', 'بِٱلْءَايَٰتِ'),
        ('رَبَّٰنِيِّـۧنَ', 'رَبَّٰنِيِّۦنَ'),
        ('لَـَٔاتٍ', 'لَءَاتٍ'),
        ('لَـَٔاتَوْهَا', 'لَءَاتَوْهَا'),
        ('لَـَٔاتَيْنَا', 'لَءَاتَيْنَا'),
        ('لَـَٔاتِيَةٌ', 'لَءَاتِيَةٌ'),
        ('لَـَٔاتِيَنَّهُم', 'لَءَاتِيَنَّهُم'),
        ('لَـَٔاكِلُونَ', 'لَءَاكِلُونَ'),
        ('لَـَٔامَنَ', 'لَءَامَنَ'),
        ('لَـَٔايَةً', 'لَءَايَةً'),
        ('لَـَٔايَٰتٍ', 'لَءَايَٰتٍ'),
        ('لَلْـَٔاخِرَةَ', 'لَلْءَاخِرَةَ'),
        ('لِـَٔابَآئِهِمْ', 'لِءَابَآئِهِمْ'),
        ('لِـَٔادَمَ', 'لِءَادَمَ'),
        ('لِـَٔايَٰتِنَا', 'لِءَايَٰتِنَا'),
        ('لِلْحَوَارِيِّـۧنَ', 'لِلْحَوَارِيِّۦنَ'),
        ('لِيَسُـۥٓـُٔوا۟', 'لِيَسُۥٓـُٔوا۟'),
        ('لَّـَٔاتَيْنَٰهُم', 'لَّءَاتَيْنَٰهُم'),
        ('لِّلْـَٔاخِرِينَ', 'لِّلْءَاخِرِينَ'),
        ('لِّلْـَٔاكِلِينَ', 'لِّلْءَاكِلِينَ'),
        ('لِّنُحْـِۧىَ', 'لِّنُحْۦِىَ'),
        ('نُـۨجِى', 'نُۨجِى'),
        ('وَبِٱلْـَٔاخِرَةِ', 'وَبِٱلْءَاخِرَةِ'),
        ('وَلَـَٔامُرَنَّهُمْ', 'وَلَءَامُرَنَّهُمْ'),
        ('وَلَلْـَٔاخِرَةُ', 'وَلَلْءَاخِرَةُ'),
        ('وَلِـِّۧىَ', 'وَلِۦِّىَ'),
        ('وَٱلنَّبِيِّـۧنَ', 'وَٱلنَّبِيِّۦنَ'),
        ('وَٱلْأُمِّيِّـۧنَ', 'وَٱلْأُمِّيِّۦنَ'),
        ('وَٱلْـَٔاخِرَةَ', 'وَٱلْءَاخِرَةَ'),
        ('وَٱلْـَٔاخِرَةُ', 'وَٱلْءَاخِرَةُ'),
        ('وَٱلْـَٔاخِرَةِ', 'وَٱلْءَاخِرَةِ'),
        ('وَٱلْـَٔاخِرُ', 'وَٱلْءَاخِرُ'),
        ('وَٱلْـَٔاخِرِينَ', 'وَٱلْءَاخِرِينَ'),
        ('وَٱلْـَٔاصَالِ', 'وَٱلْءَاصَالِ'),
        ('يَٰصَٰحِبَىِ', 'يَٰصَىٰحِبَىِ'),
        ('يُحْـِۧىَ', 'يُحْۦِىَ'),
        ('ٱلنَّبِيِّـۧنَ', 'ٱلنَّبِيِّۦنَ'),
        ('ٱلْأُمِّيِّـۧنَ', 'ٱلْأُمِّيِّۦنَ'),
        ('ٱلْحَوَارِيِّـۧنَ', 'ٱلْحَوَارِيِّۦنَ'),
        ('ٱلْـَٔاثِمِينَ', 'ٱلْءَاثِمِينَ'),
        ('ٱلْـَٔاخَرُ', 'ٱلْءَاخَرُ'),
        ('ٱلْـَٔاخَرِ', 'ٱلْءَاخَرِ'),
        ('ٱلْـَٔاخَرِينَ', 'ٱلْءَاخَرِينَ'),
        ('ٱلْـَٔاخِرَ', 'ٱلْءَاخِرَ'),
        ('ٱلْـَٔاخِرَةَ', 'ٱلْءَاخِرَةَ'),
        ('ٱلْـَٔاخِرَةُ', 'ٱلْءَاخِرَةُ'),
        ('ٱلْـَٔاخِرَةِ', 'ٱلْءَاخِرَةِ'),
        ('ٱلْـَٔاخِرِ', 'ٱلْءَاخِرِ'),
        ('ٱلْـَٔاخِرِينَ', 'ٱلْءَاخِرِينَ'),
        ('ٱلْـَٔازِفَةُ', 'ٱلْءَازِفَةُ'),
        ('ٱلْـَٔازِفَةِ', 'ٱلْءَازِفَةِ'),
        ('ٱلْـَٔافَاقِ', 'ٱلْءَافَاقِ'),
        ('ٱلْـَٔافِلِينَ', 'ٱلْءَافِلِينَ'),
        ('ٱلْـَٔالِهَةَ', 'ٱلْءَالِهَةَ'),
        ('ٱلْـَٔامِرُونَ', 'ٱلْءَامِرُونَ'),
        ('ٱلْـَٔامِنِينَ', 'ٱلْءَامِنِينَ'),
        ('ٱلْـَٔانَ', 'ٱلْءَانَ'),
        ('ٱلْـَٔايَةَ', 'ٱلْءَايَةَ'),
        ('ٱلْـَٔايَٰتُ', 'ٱلْءَايَٰتُ'),
        ('ٱلْـَٔايَٰتِ', 'ٱلْءَايَٰتِ'),
    ]

    manual_pairs = [('طه', 'طه'),
                    ('ۖ', 'ۖ'),
                    ('ۗ', 'ۗ'),
                    ('ۘ', 'ۘ'),
                    ('ۙ', 'ۙ'),
                    ('ۚ', 'ۚ'),
                    ('ۛ', 'ۛ'),
                    ('ۜ', 'ۜ'),
                    ('۞', '۞'),
                    ('۩', '۩')]

    # Convert uth_to_simple_pairs to a dictionary for quick lookup
    uth_ref_lookup = dict(uth_to_simple_pairs)

    # Update pairs using the manual Tanzil Uthmani to Reference Uthmani mapping
    updated_pairs = [
        (tanzil_uth, uth_ref_lookup[ref_uth])
        for tanzil_uth, ref_uth in manual_tanzil_uth_to_ref_uth
        if ref_uth in uth_ref_lookup
    ]

    # Extend the original list with both updated and manual pairs
    uth_to_simple_pairs.extend(updated_pairs + manual_pairs)
    return uth_to_simple_pairs  # [(uthmani, simple)..]


if __name__ == "__main__":
    quran_text_to_font = generate_aligned_pairs()

    pairs = load_uthmani_to_simple_pairs()
    uth_to_simple = dict(pairs)
    missing_uthmani_from_tanzil = set()
    found_uthmani_in_mapper = set()
    for aya in quran_text_to_font:
        for token in aya["uthmani_tokens"]:
            if token in uth_to_simple:
                found_uthmani_in_mapper.add(token)
            else:
                missing_uthmani_from_tanzil.add(token)

    unused_in_mapper = set(uth_to_simple.keys()).difference(found_uthmani_in_mapper)
    assert len(missing_uthmani_from_tanzil) == 0  # if this passes this means we have the full one-to-one mapping from uthmani to simple

    for entry in quran_text_to_font:
        entry["simple"] = [uth_to_simple[w] for w in entry["uthmani_tokens"]]

    with open('resources/quran_text_to_font.json', 'w') as f:
        json.dump(quran_text_to_font, f)
    print("resources/quran_text_to_font.json has been saved")
