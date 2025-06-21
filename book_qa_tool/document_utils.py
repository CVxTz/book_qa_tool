import random
from pathlib import Path
from typing import List

from pdf2image import convert_from_bytes
from PIL import Image
from pypdf import PdfReader

from book_qa_tool.logger import logger


def extract_images_from_pdf(
    pdf_path: Path, first_page: int = None, last_page: int = None
):
    """
    Extracts images from a PDF file.

    Args:
        pdf_path (Path): The path to the PDF file.
        first_page (int, optional): The first page to extract (1-indexed). Defaults to None (start from the beginning).
        last_page (int, optional): The last page to extract (1-indexed). Defaults to None (extract to the end).

    Returns:
        List[PIL.Image.Image]: A list of PIL Image objects.
    """
    logger.info(f"Extracting images from PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        # We don't write to disk, so a temporary directory isn't strictly needed for output_folder
        # with convert_from_bytes, but it's good practice if there were intermediate files.
        # However, convert_from_bytes itself does not write to output_folder when returning PIL images.
        images = convert_from_bytes(
            pdf_file=f.read(), first_page=first_page, last_page=last_page, fmt="jpeg"
        )
        logger.info(f"Extracted {len(images)} images from the PDF.")
        return images


def extract_text_from_pdf(pdf_path: Path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (Path): The path to the PDF file.

    Returns:
        List[str]: A list of strings, where each string is the text from a page.
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        logger.info(f"Extracting text from {len(reader.pages)} pages.")
        texts = [page.extract_text() for page in reader.pages]
        logger.info(f"Extracted text from {len(texts)} pages.")
        return texts


def extract_random_k_consecutive_pages_as_images(
    folder_path: Path, k: int
) -> List[Image.Image]:
    """
    Extracts a random k consecutive pages from a random PDF in a folder as images.
    If the selected PDF has less than k pages, all of its pages are extracted.

    Args:
        folder_path (Path): The path to the folder containing PDF files.
        k (int): The number of consecutive pages to extract.

    Returns:
        List[PIL.Image.Image]: A list of PIL Image objects representing the extracted pages.

    Raises:
        ValueError: If no PDF files are found in the specified folder.
    """
    pdf_files = list(folder_path.glob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDF files found in the folder: {folder_path}")

    random_pdf_path = random.choice(pdf_files)
    logger.info(f"Selected random PDF: {random_pdf_path}")

    with open(random_pdf_path, "rb") as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)

    if total_pages <= k:
        logger.info(
            f"PDF has {total_pages} pages, which is less than or equal to k ({k}). Extracting all pages."
        )
        return extract_images_from_pdf(random_pdf_path)
    else:
        start_page_index = random.randint(0, total_pages - k)
        first_page = start_page_index + 1  # convert to 1-indexed
        last_page = first_page + k - 1
        logger.info(
            f"Extracting {k} consecutive pages from page {first_page} to {last_page}."
        )
        return extract_images_from_pdf(
            random_pdf_path, first_page=first_page, last_page=last_page
        )
