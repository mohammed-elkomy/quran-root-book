# How to visualize Quran fonts

- first you need to generate quran_text_to_font.json triplets file from the quran_data.py script

  ```bash
  python quran_data.py 
  ```

- This will save the triplets in the 'font demo' folder

- after that you can generate HTML to visualize the fonts
- for example for sura_no=5 and aya_no=8 the *generate_samply.py* script

  ```python
  generate_html_with_hover(sura_no=5, aya_no=8)
  ```