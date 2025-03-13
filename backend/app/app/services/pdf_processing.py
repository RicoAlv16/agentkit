import asyncio
from some_pdf_library import process_pdf

async def process_pdf_async(file_path):
    result = await asyncio.to_thread(process_pdf, file_path)
    return result

# Usage
asyncio.run(process_pdf_async('path/to/pdf'))

# ... existing code ...