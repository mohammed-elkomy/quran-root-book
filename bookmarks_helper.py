from collections import defaultdict

from reportlab.platypus import Table

from config import IS_ARABIC, ROOT_BG_COLOR, SINGLE_COLUMN


# Simulate the nested dictionary structure
def build_nested_structure(entries):
    nested_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Loop through the list of tuples
    for page, arabic_text in entries:
        first_char, second_char, third_char = arabic_text.split()

        # Create a three-level nested dictionary structure
        nested_dict[first_char][second_char][third_char] = page

    return nested_dict


def add_page_bookmarks(canvas, doc, bookmarks_lookup):
    for key_idx, keys in enumerate(bookmarks_lookup[doc.page]):
        if keys is None:
            keys = ["Root"]
            level = 0
        else:
            level = len(keys)

        canvas.bookmarkPage(f"page_{doc.page}_{key_idx}_{" ".join(keys)}")
        last_char = keys[-1]
        if IS_ARABIC:
            canvas.addOutlineEntry(last_char, f"page_{doc.page}_{key_idx}_{" ".join(keys)}", level=level)

    if not IS_ARABIC and doc.page == max(bookmarks_lookup.keys()):
        reorder_bookmarks = []
        for current_page in bookmarks_lookup:
            for key_idx, keys in enumerate(bookmarks_lookup[current_page]):
                reorder_bookmarks.append((keys, key_idx, current_page))

        reorder_bookmarks.sort(key=lambda item: "-".join(item[0]) if item[0] else "")
        for keys, key_idx, current_page in reorder_bookmarks:
            if keys is None:
                keys = ["Root"]
                level = 0
            else:
                level = len(keys)

            canvas.addOutlineEntry(keys[-1], f"page_{current_page}_{key_idx}_{" ".join(keys)}", level=level)


def extract_root_tables_from_super_table(table, ):
    root_tables_cols_num = 7 if SINGLE_COLUMN else 3
    center_idx = root_tables_cols_num // 2
    found_root_subtables = []
    for row in table._cellvalues:
        for cell in row:
            for element in cell:
                if isinstance(element, Table) and element._ncols == root_tables_cols_num and element._bkgrndcmds[-1][-1] == ROOT_BG_COLOR:
                    found_root_subtables.append(element)
    roots_in_page = []
    for table in found_root_subtables:
        root_text = table._cellvalues[1 if IS_ARABIC else 0][center_idx][0].text
        font_name = table._cellvalues[1 if IS_ARABIC else 0][center_idx][0].style.fontName
        roots_in_page.append((font_name, root_text))
    return roots_in_page
