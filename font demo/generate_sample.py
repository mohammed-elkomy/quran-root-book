import json

# Sample input JSON list
json_data = json.load(open("quran_text_to_font.json"))


def generate_html_with_hover(sura_no, aya_no, output_file="output_with_hover.html"):
    # Search for the requested sura_no and aya_no in the json data
    for entry in json_data:
        if entry["sura_no"] == sura_no and entry["aya_no"] == aya_no:
            uthmani_tokens = entry["uthmani_tokens"]
            simple_tokens = entry["simple"]
            font_symbols = entry["font_symbols"]
            font_id = entry["font_id"]

            # Generate the HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sura {sura_no}, Aya {aya_no}</title>
                <style>
                    @font-face {{
                        font-family: "{font_id}";
                        src: url("fonts/{font_id}.ttf");
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        direction: rtl;
                    }}
                    td {{
                        text-align: center;
                        padding: 10px;
                        border: 1px solid #ddd;
                        cursor: pointer;
                    }}
                    .font-symbol {{
                        font-family: "{font_id}";
                        font-size: 32px;
                    }}
                    .uthmani-token {{
                        font-size: 24px;
                    }}
                    td:hover {{
                        background-color: gray;
                    }}
                </style>
            </head>
            <body>
                <div>
                    <h1>Sura {sura_no}, Aya {aya_no}</h1>
                    <table>
                        <tr>
                            <!-- Simple Tokens Row -->
                            {''.join([f'<td class="uthmani-token">{token}</td>' for token in simple_tokens])}
                        </tr>
                        <tr>
                            <!-- Uthmani Tokens Row -->
                            {''.join([f'<td class="uthmani-token">{token}</td>' for token in uthmani_tokens])}
                        </tr>
                        <tr>
                            <!-- Font Symbols Row -->
                            {''.join([f'<td>{symbol}</td>' for symbol in font_symbols])}
                        </tr>
                        <tr>
                            <!-- Font Symbols Row rendered -->
                            {''.join([f'<td class="font-symbol">{symbol}</td>' for symbol in font_symbols])}
                        </tr>
                    </table>
                </div>
            </body>
            </html>
            """

            # Write the HTML content to an output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML file generated: {output_file}")
            return

    print(f"No entry found for Sura {sura_no}, Aya {aya_no}")


# Example usage:
# those sura ids and aya ids were problematic in the fonts collection
# please don't delete those samples
generate_html_with_hover(sura_no=69, aya_no=8)
generate_html_with_hover(sura_no=13, aya_no=37)
generate_html_with_hover(sura_no=2, aya_no=79)

generate_html_with_hover(sura_no=5, aya_no=8)
