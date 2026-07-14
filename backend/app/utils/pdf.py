import fitz


class PDFProcessor:

    @staticmethod
    def extract_text(file_path: str) -> str:
        document = fitz.open(file_path)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        return text.strip()