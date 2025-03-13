import asyncio
from concurrent.futures import ThreadPoolExecutor
from pdfminer.high_level import extract_text
import mmap

async def process_pdf_async(file_path: str) -> str:
    """Process PDF asynchronously using memory-mapped files."""
    loop = asyncio.get_event_loop()
    with open(file_path, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mapped_file:
            return await loop.run_in_executor(None, extract_text, mapped_file)

async def _load_docs_async(dir_path: str) -> list:
    """Process PDFs in parallel using async tasks."""
    pdf_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".pdf")]

    # Process PDFs concurrently
    texts = await asyncio.gather(*(process_pdf_async(f) for f in pdf_files))

    return [Document(content=text, metadata={"source": pdf}) for pdf, text in zip(pdf_files, texts)]

# ... existing code ...