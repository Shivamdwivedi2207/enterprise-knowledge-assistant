from app.utils.pdf import PDFProcessor

text = PDFProcessor.extract_text(
    "storage/uploads/851a4c99-5896-4ff9-ad75-bee94e32244e.pdf"
)

print(text[:1000])

