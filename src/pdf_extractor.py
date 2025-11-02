"""
📄 MODULE 2: PDF EXTRACTION
===========================

Extracts text from PDF files fetched from URLs.

KEY CONCEPTS:
- HTTP requests to fetch the PDF from the URL
- PyPDF2: for extracting text from the PDF
- Error Handling: for handling errors during PDF fetching and text extraction
"""

import requests
import PyPDF2
from io import BytesIO
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf_url(pdf_url, timeout=30):
    """
    Fetches a PDF from the given URL and extracts its text content.
    
    Args:
        pdf_url (str): The URL of the PDF to fetch.
        timeout (int): Timeout for the HTTP request in seconds (how long to wait for download).
        
    Returns:
        str: Extracted text from the PDF.
        or None if extraction fails.
    """
    try:
        logger.info(f"📥 Fetching PDF from URL: {pdf_url}")
        response = requests.get(pdf_url, timeout=timeout)
        response.raise_for_status()  # Raise an error for bad responses
        
        logger.info(f"✅ PDF downloaded successfully")
        
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        total_pages = len(pdf_reader.pages)
        logger.info(f"📖 Extracting text from {total_pages} pages...")
        
        # FIX: Iterate over pdf_reader.pages, not total_pages (which is an int)
        for i, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                
                if page_text:
                    text += page_text + "\n"
                
                # Log progress every 10 pages
                if (i + 1) % 10 == 0:
                    logger.info(f"  ... extracted page {i+1}/{total_pages}")
            
            except Exception as page_error:
                logger.warning(f"⚠️ Could not extract page {i + 1}: {page_error}")
                continue
        
        # FIX: Clean text AFTER loop, not inside
        text = text.replace('\n', ' ').strip()
        text = ' '.join(text.split())  # Remove extra whitespace
        
        if not text:
            logger.warning(f"⚠️ No text extracted from PDF: {pdf_url}")
            return None
        
        logger.info(f"✅ Successfully extracted {len(text)} characters from {total_pages} pages")
        return text
    
    except requests.exceptions.Timeout:
        logger.error("⏰ PDF download timed out.")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("🔌 Connection error while fetching PDF from URL")
        return None
    except Exception as e:
        logger.error(f"❌ Error extracting text from PDF: {e}")
        return None


# FIX: Function name was typo'd
def truncate_text(text, max_tokens=1024):
    """
    Truncate text to fit the transformer model input limit if necessary.
    
    PEGASUS can handle inputs up to ~1024 tokens (~4000 characters).
    This function ensures the limit is not exceeded.
    
    Args:
        text (str): The extracted text from the PDF.
        max_tokens (int): Maximum tokens (default: 1024).
        
    Returns:
        str: Truncated text if it exceeds max_tokens, else original text.
    """
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    
    if len(text) > max_chars:
        logger.info(f"✂️ Truncating text from {len(text)} to {max_chars} characters.")
        return text[:max_chars]
    
    return text


def clean_text(text):
    """
    Cleans the extracted text by removing excessive whitespace.
    
    Args:
        text (str): The extracted text from the PDF.
        
    Returns:
        str: Cleaned text.
    """
    text = ' '.join(text.split())  # Remove excessive whitespace
    return text


# Test function
def test_pdf_extraction():
    """
    Test PDF extraction with the Transformer paper.
    """
    print("\n" + "="*70)
    print("TEST: PDF Extraction Module")
    print("="*70)
    
    example_pdf = "https://arxiv.org/pdf/1706.03762.pdf"
    print(f"\n📥 Downloading PDF: {example_pdf}")
    print("📖 Extracting text...\n")
    
    text = extract_text_from_pdf_url(example_pdf)
    
    if text:
        print(f"\n✅ Success!")
        print(f"📊 Extracted {len(text)} characters")
        print(f"📊 Approximately {len(text.split())} words")
        print(f"\n📌 First 500 characters:\n")
        print(text[:500])
        print("\n...")
    else:
        print("\n❌ Failed to extract text")


if __name__ == "__main__":
    test_pdf_extraction()
