# Quran root index book generator

This project generates *Quran root index book* using ReportLab and data sources from Excel and XML files .
It includes support for Quranic translations (Arabic and English), font customization, and layout configurations tailored for both single and double column designs.
Quran is rendered in its original Arabic script using QPC fonts, which is never altered 💯, as used in [Quran.com](https://github.com/mustafa0x/qpc-fonts)

## Features

- Generate the Quran root index book based on an external resource file. This is an interesting research point 📚 for those who are interested in *Arabic morphology*.
- The generated report can be customized to include a specific Quranic translation (currently English supported), font, and layout.
- Bookmarks tree is generated automatically based on the input data. (Very interesting TRIE-inspired approach 🤓🤓)
- We highlight the target word for each root using fuzzy search✏️✏️.
- Translations for the Holy verse along with the target word for each root.
- The generated report can be either single or double column layout.
- The report is presented as a long table that extends to multiple pages; however, thanks to reportlab, auto-splitting is done automatically (similar to ms-word).
- We provide triplets of mappings of Uthmani, Simple and Quranic symbols. (visualize them in the 'font demo' folder)

## Tackled challenges

- Handling Arabic text in PDFs. (Broadly useful for the RTL languages)
- Rendering the Holy Quran in custom QPC fonts. (The standard fonts for the Holy Quran render individual *words* rather than charters as in the usual fonts)
- Generating the index automatically according to the layout
- Single and column layouts
- Word highlighting with fuzzy search (weak matches are reported as warnings)
- Translation support
- Auto-splitting of the long table
- External authentic resources from Tanzil and QPC fonts are used to guarantee the Holy Quran is never altered. 🤗

## Future challenges

- Unfortunately, due to the way the Quranic fonts are presented, we can not enable copy and paste functionality for the generated PDF.
  This can be addressed:
    - By adding an extra layer in the PDF, but this can be quite inefficient for the end user.
    - By using a different pdf viewer with custom support for copying and pasting.
      For example, Okular, an open source pdf previewer, can be adapted to be Quran-aware and the copy and paste functions are intervened by mapping the copied character the target text from the triplets mappings.

- Allow translations to be in any language supporting R2L and L2R alike.

## Table of Contents

- [Project Structure](#project-structure)
- [Configuration Options](#configuration-options)
    - [Input and Output Paths](#input-and-output-paths)
    - [Metadata and Fonts](#metadata-and-fonts)
    - [Color Options](#color-options)
    - [Layout Options](#layout-options)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [Output File Naming Convention](#output-file-naming-convention)

---

## Project Structure

This project’s main configurations can be found in the configuration section of the `config.py` script. Configuration includes options for file paths, font choices, color schemes, and layout preferences. The `resources` folder stores the required input files for PDF generation, such as fonts, data, and XML documents.

## Configuration Options

The configuration options are organized into different categories:

### Input and Output Paths

- **`INPUT_DATA`**: Path to the main Excel data file (`data.xlsx`).
- **Resource Files**:
    - **MUSHAF_RES**: Path to `mushaf.txt` for Quran text. ([Taken from this repo](https://github.com/mustafa0x/qpc-fonts/blob/master/mushaf.txt))
    - **MUSHAF_META**: Path to metadata for the Quran (`quran-data.xml`). ([From tanzil](https://tanzil.net/docs/quran_metadata))
    - **QURAN_TEXT**: Path to Quranic text in Uthmani script (`quran-uthmani.xml`). ([From tanzil (hizb symbol is included)](https://tanzil.net/download/))
    - **UTH_TO_SIMPLE**: Uthmani to Simple mapping (`Uthmani to Simple Mapping.html`). ([From qurananalysis.com](https://www.qurananalysis.com/analysis/uthmani-to-simple.php))
    - **TRANSLATION_XML**: Translation file path (`english_translation.xml`).  ([From tanzil translations](https://tanzil.net/trans/))

### Metadata and Fonts

- **PDF Metadata**: Configure the generated PDF's metadata, such as title, author, subject, keywords, and creator.
- **Fonts**:
    - **GENERAL_ARABIC_FONT**: Arabic font selection.
    - **GENERAL_NON_ARABIC_FONT**: The non-Arabic font selection used for translation, English for example.
    - **Font Sizes**: Customize Quran font size (`QURAN_FONT_SIZE`) and general font sizes for Arabic (`GENERAL_FONT_SIZE_AR`) and Translation (English for example) (`GENERAL_FONT_SIZE_NON_AR`).

### Color Options

Customize the colors for various PDF components:

- **ROOT_HEADER_BK_COLOR**: Background color for headers.
- **TABLE_BK_COLOR**: Background color for tables.
- **ROOT_BORDER_COLOR**: Color for borders.
- **ROOT_BG_COLOR**: General background color for the PDF layout.

### Layout Options

- **Language Settings**:
    - Set `IS_ARABIC` to `True` for Arabic or `False` for non-Arabic (Currently English only is supported).
    - Adjust header names based on the language setting.
- **Table Padding**: Customize padding for tables and headers.
- **Column Layouts**:
  This sets the relative width for each column
    - **HEADER_TABLE_RATIOS_DOUBLE** and **GENERAL_TABLE_RATIOS_DOUBLE** for double-column layouts.
    - **HEADER_TABLE_RATIOS_SINGLE** and **GENERAL_TABLE_RATIOS_SINGLE** for single-column layouts.
    - **SINGLE_COLUMN**: Set to `True` for single-column layout, `False` for double-column.
- **Miscellaneous**:
    - **DATA_REPEAT_MULTIPLIER**: Multiplier for data repetition (useful for testing).

## Installation

1. Clone the repository and navigate to its directory.
2. Install dependencies with:
   ```bash
   pip install -r requirements.txt
   ``` 

## Docker

You can simply run: (root access might be needed)

   ```bash
   ./docker_demo.sh
   ```

## Usage

1. First, modify the configurations in the config.py file
2. Then, to generate the PDF report, assuming all resource file are found, simply run:

```bash
python main.py
```

## Requirements

Dependencies are listed in requirements.txt. Run pip install -r requirements.txt to install them.

## Output File Naming Convention

The output is saved the `output` directory. The output file name will be in the format: `{current_date}-report.pdf`.

```
YYYYMMDD_column_layout_language_row_separator.pdf
```

Where:

- `YYYYMMDD` is the current date in the format `YYYYMMDD`.
- `column_layout` is either `single` or `double`.
- `language` is either `ar` or `non-arabic`.
- `row_separator` is either `true` or `false`.

For example, an output file might be named `20231024_double_arabic_nosep.pdf`.

## Contributing

If you would like to contribute to this project, please submit a pull request or open an issue.