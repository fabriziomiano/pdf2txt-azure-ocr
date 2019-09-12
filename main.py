import os
import argparse
import logging
from io import BytesIO
from utils.misc import get_logger, extract_text_from_unsearchable_pdf
logger = get_logger(__name__)
logger.setLevel(logging.INFO)


def process_file(file_path):
    """
    Extract the text from a given file
    :param file_path: str absolute file path
    :return: str
    """
    with open(file_path, 'rb') as file_in:
        pdf_byte_content = BytesIO(file_in.read())
        corpus = extract_text_from_unsearchable_pdf(pdf_byte_content)
        return corpus


def main(dir_path):
    """
    Process all the PDF files in a given dir and  write
    their content in .txt files, inheriting the filenames.
    :param dir_path: str input directory
    :return: None
    """
    logger.info("Reading from {0}".format(dir_path))
    for filename in os.listdir(dir_path):
        if filename.endswith('.pdf'):
            logger.info("Processing file {}".format(filename))
            file_path = os.path.join(dir_path, filename)
            corpus = process_file(file_path)
            txt_file = filename.replace('pdf', 'txt')
            logger.info("Saving file {}".format(txt_file))
            with open(txt_file, 'w') as file_out:
                file_out.write(corpus)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-dp', '--dirpath',
        type=str,
        metavar='',
        required=True,
        help="Specify the dir path containing the docs to convert to txt"
    )
    ARGS = parser.parse_args()
    DIR_PATH = ARGS.dirpath
    logger.info("selected {}".format(DIR_PATH))
    main(DIR_PATH)
