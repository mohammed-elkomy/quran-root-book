import logging

from config import INPUT_DATA, OUTPUT_PDF
from pdf_generation import generate_pdf

if __name__ == "__main__":
    # Set up basic logging configuration
    logging.basicConfig(
        level=logging.DEBUG,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    generate_pdf(source_path=INPUT_DATA,
                 output_path=OUTPUT_PDF)
