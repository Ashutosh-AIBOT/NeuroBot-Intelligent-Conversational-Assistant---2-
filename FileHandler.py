import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import json
from datetime import datetime

# Optional fallback imports
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from pdfminer.high_level import extract_text as pdfminer_extract
except ImportError:
    pdfminer_extract = None


class FileHandler:
    """Handles file uploads, text extraction, and JSON-based storage."""

    def __init__(self, upload_dir="uploads", json_dir="processed_json"):
        self.upload_dir = upload_dir
        self.json_dir = json_dir

        # Subfolders for organization
        self.subfolders = {
            "pdf": os.path.join(self.json_dir, "pdf_files"),
            "image": os.path.join(self.json_dir, "image_files"),
            "text": os.path.join(self.json_dir, "text_files"),
        }

        # Create necessary folders
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        for folder in self.subfolders.values():
            os.makedirs(folder, exist_ok=True)

    # --------------------------------------------
    # Save uploaded file locally
    # --------------------------------------------
    def save_uploaded_file(self, uploaded_file):
        try:
            file_path = os.path.join(self.upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            print(f"[INFO] ✅ File saved at: {file_path}")
            return file_path
        except Exception as e:
            print(f"[ERROR] ❌ File save failed: {e}")
            return None

    # --------------------------------------------
    # Extract PDF text (page by page)
    # --------------------------------------------
    def extract_text_from_pdf(self, file_path):
        pages = []
        try:
            with fitz.open(file_path) as pdf:
                for i, page in enumerate(pdf, start=1):
                    text = page.get_text("text").strip()
                    pages.append({"page": i, "text": text})
            return pages
        except Exception as e:
            print(f"[WARN] PyMuPDF failed: {e}")

        # Fallbacks
        if PdfReader:
            try:
                with open(file_path, "rb") as f:
                    reader = PdfReader(f)
                    for i, page in enumerate(reader.pages, start=1):
                        text = (page.extract_text() or "").strip()
                        pages.append({"page": i, "text": text})
                if pages:
                    return pages
            except Exception as e:
                print(f"[WARN] PyPDF2 failed: {e}")

        if pdfminer_extract:
            try:
                mined_text = pdfminer_extract(file_path)
                if mined_text.strip():
                    pages = [{"page": 1, "text": mined_text.strip()}]
                    return pages
            except Exception as e:
                print(f"[WARN] pdfminer failed: {e}")

        # OCR fallback
        try:
            import pdf2image
            images = pdf2image.convert_from_path(file_path)
            for i, img in enumerate(images, start=1):
                text = pytesseract.image_to_string(img).strip()
                pages.append({"page": i, "text": text})
            return pages
        except Exception as e:
            print(f"[ERROR] OCR extraction failed: {e}")

        return []

    # --------------------------------------------
    # Extract image text
    # --------------------------------------------
    def extract_text_from_image(self, file_path):
        try:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img).strip()
        except Exception as e:
            print(f"[ERROR] Image extraction failed: {e}")
            return ""

    # --------------------------------------------
    # Extract text from TXT
    # --------------------------------------------
    def extract_text_from_txt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read().strip()
            except Exception as e:
                print(f"[ERROR] TXT extraction failed: {e}")
                return ""

    # --------------------------------------------
    # Save JSON output (one per PDF)
    # --------------------------------------------
    def save_json_output(self, filename, data, file_type="general"):
        try:
            base_name = os.path.splitext(os.path.basename(filename))[0]
            subfolder = self.subfolders.get(file_type.lower(), self.json_dir)
            os.makedirs(subfolder, exist_ok=True)

            # ✅ Only one JSON per file: overwrite if exists
            json_path = os.path.join(subfolder, f"{base_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[INFO] 💾 JSON saved at: {json_path}")
            return json_path
        except Exception as e:
            print(f"[ERROR] Failed to save JSON: {e}")
            return None

    # --------------------------------------------
    # Master Processor
    # --------------------------------------------
    def process_file(self, uploaded_file):
        if not uploaded_file:
            return {"status": "error", "error": "No file uploaded."}

        file_path = self.save_uploaded_file(uploaded_file)
        if not file_path:
            return {"status": "error", "error": "Failed to save file."}

        filename = uploaded_file.name.lower()
        result_data = {}
        try:
            if filename.endswith(".pdf"):
                pages = self.extract_text_from_pdf(file_path)
                if not pages:
                    raise ValueError("No text extracted from PDF.")

                total_pages = len(pages)
                result_data = {
                    "file_name": uploaded_file.name,
                    "type": "PDF",
                    "total_pages": total_pages,
                    "pages": pages,
                    "timestamp": datetime.now().isoformat(),
                }

                # ✅ Single JSON per PDF
                json_path = self.save_json_output(uploaded_file.name, result_data, "pdf")

            elif filename.endswith((".png", ".jpg", ".jpeg")):
                text = self.extract_text_from_image(file_path)
                result_data = {
                    "file_name": uploaded_file.name,
                    "type": "Image",
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                }
                json_path = self.save_json_output(uploaded_file.name, result_data, "image")

            elif filename.endswith(".txt"):
                text = self.extract_text_from_txt(file_path)
                result_data = {
                    "file_name": uploaded_file.name,
                    "type": "Text",
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                }
                json_path = self.save_json_output(uploaded_file.name, result_data, "text")

            else:
                return {"status": "error", "error": "Unsupported file type."}

        except Exception as e:
            return {"status": "error", "error": str(e)}

        return {
            "status": "success",
            "data": result_data,
            "json_path": json_path,
            "local_path": file_path,
        }

    # --------------------------------------------
    # Validate page range (strict)
    # --------------------------------------------
    @staticmethod
    def validate_page_range(start, end, total_pages):
        if start < 1:
            start = 1
        if end > total_pages:
            end = total_pages
        if start > end:
            start = end
        return start, end
