from app.utils.pdf import PDFProcessor
from app.utils.text_splitter import TextSplitter

# Replace with an actual file inside storage/uploads
pdf_path = "storage/uploads/851a4c99-5896-4ff9-ad75-bee94e32244e.pdf"

text = PDFProcessor.extract_text(pdf_path)

splitter = TextSplitter()

chunks = splitter.split(text)

print(f"Total Chunks: {len(chunks)}")

print("\nFirst Chunk:\n")
print(chunks[0])

print("\nSecond Chunk:\n")
print(chunks[1] if len(chunks) > 1 else "No second chunk")

