from PyPDF2 import PdfFileWriter, PdfFileReader
from pdf2image import convert_from_path
import logging
import requests
from io import BytesIO
import os


def get_logger(name):
    """
    Add a StreamHandler to a logger if still not added and
    return the logger

    :param name: str
    :return: logger.logger object
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.propagate = 1  # propagate to parent
        console = logging.StreamHandler()
        logger.addHandler(console)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s [%(levelname)s] %(message)s')
        console.setFormatter(formatter)
    return logger


LOGGER = get_logger(__name__)
LOGGER.setLevel(logging.INFO)


def azure_ocr(pil_image):
    """
    Return a string containing the text that has been ocred
    from a given page of a pdf.
    :param pil_image: PIL Image
    :return: str
    """
    api_url = (
        "https://westeurope.api.cognitive.microsoft.com/vision/v2.0/ocr"
    )
    header = {
        'Ocp-Apim-Subscription-Key': 'YOUR_KEY',
        'Content-Type': 'application/octet-stream'
    }
    params = {'language': 'it'}
    try:
        img = pil_image
        bin_img = BytesIO()
        img.save(bin_img, format='JPEG')
        img.close()
        img_data = bin_img.getvalue()
        bin_img.close()
        r = requests.post(
            api_url,
            params=params,
            headers=header,
            data=img_data
        )
        r.raise_for_status()
        data = r.json()
        text = ''
        for item in data['regions']:
            for line in item['lines']:
                for word in line['words']:
                    text += ' ' + word['text']
        return text
    except Exception as e:
        LOGGER.error(e)
        return ''


def pdf_splitter(stream_in):
    """
    Split a PDF into a N files where N is the number of pages.
    :param stream_in: bytes
    :return: list of absolute file paths
    """
    pdf_files = []
    reader = PdfFileReader(stream_in)
    writer = PdfFileWriter()
    for page in range(reader.getNumPages()):
        writer.addPage(reader.getPage(page))
        output_filename = 'tmp_{}.pdf'.format(page+1)
        with open(output_filename, 'wb') as out:
            writer.write(out)
            LOGGER.info('Created: {}'.format(output_filename))
        pdf_files.append(output_filename)
    return pdf_files


def delete_files(file_list):
    """
    Delete all the files in a given dir
    :param file_list: list of absolute file paths
    :return: None
    """
    """
    Delete a sequence of files within a given list of paths
    """
    try:
        for filename in file_list:
            LOGGER.info('Removed: {}'.format(filename))
            os.remove(filename)
    except OSError:
        pass


def extract_text_from_unsearchable_pdf(stream_in):
    """
    Return a string containing the text present in a given PDF
    :param stream_in: bytes
    :return: str
    """
    file_list = pdf_splitter(stream_in)
    text = ""
    for single_pdf in file_list:
        image_from_path = convert_from_path(single_pdf, fmt='jpg')[0]
        text += azure_ocr(image_from_path)
    delete_files(file_list)
    return text
