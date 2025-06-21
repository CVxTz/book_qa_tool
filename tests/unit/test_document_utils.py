from pathlib import Path

from PIL import Image

from book_qa_tool.document_utils import (
    extract_images_from_pdf,
    extract_random_k_consecutive_pages_as_images,
    extract_text_from_pdf,
)


# Test for extract_images_from_pdf
def test_extract_images_from_pdf():
    pdf_file = Path(__file__).parents[2] / "data" / "docs.pdf"
    images = extract_images_from_pdf(pdf_file)
    assert len(images) > 0, "Expected at least one image in the PDF"
    assert all(
        image.format == "JPEG" for image in images
    ), "Images should be in JPEG format"


# Test for extract_text_from_pdf
def test_extract_text_from_pdf():
    pdf_file = Path(__file__).parents[2] / "data" / "docs.pdf"
    texts = extract_text_from_pdf(pdf_file)
    assert len(texts) > 0, "Expected text from at least one page"
    for page_text in texts:
        assert page_text.strip(), "Extracted text should not be empty"


# Test for extract_random_k_consecutive_pages_as_images
def test_extract_random_k_consecutive_pages_as_images():
    # Define the folder path where docs.pdf is located
    folder_path = Path(__file__).parents[2] / "data"
    # Choose a value for k, the number of consecutive pages to extract
    k = 3
    # Call the function to extract random k consecutive pages
    extracted_images = extract_random_k_consecutive_pages_as_images(folder_path, k)

    # Assertions to verify the function's behavior
    assert len(extracted_images) > 0, "Expected at least one image to be extracted."
    # The number of extracted images should be less than or equal to k,
    # respecting the function's rule about extracting all pages if total_pages < k.
    assert (
        len(extracted_images) <= k
    ), f"Expected at most {k} images, but got {len(extracted_images)}."
    # Verify that all items in the list are actual PIL Image objects
    assert all(
        isinstance(image, Image.Image) for image in extracted_images
    ), "All extracted items should be PIL Image objects."
    # Verify that the extracted images are in JPEG format, consistent with other tests
    assert all(
        image.format == "JPEG" for image in extracted_images
    ), "All extracted images should be in JPEG format."
