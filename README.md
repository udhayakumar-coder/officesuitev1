# All21Tool V2 — Professional PDF & Image Studio

A Streamlit application built from the uploaded All21Tool repository. The existing PDF engine and tools are retained, the unfinished UI for tool 21 is completed, and a new Image Studio is added.

## Included features

### PDF Studio — original 21 tools retained
1. Merge PDFs
2. Split / Extract Pages
3. Rotate, Reorder & Delete Pages
4. Crop PDF Pages
5. Add Stamp / Signature
6. Watermark & Page Numbers
7. Lock PDF (AES-256)
8. Unlock PDF (requires the correct password)
9. Smart Redact (phone, Aadhaar-like number, email, custom terms)
10. Metadata Cleaner
11. Smart Compress
12. Batch Compress
13. Batch Watermark
14. A4 Sheet Imposition (2-Up / 4-Up)
15. Extract Embedded Images
16. Images to PDF
17. PDF to Images
18. OCR Text Extract (Tamil + English)
19. PDF to Word
20. PDF Tables to Excel
21. Search & Highlight / Find & Replace

### Image Studio
- Resize by pixels, percentage, centimetres or inches
- Preserve aspect ratio
- Compress toward a target KB size
- Convert PNG / JPEG / WEBP / BMP / TIFF
- Crop, rotate and flip
- Prepare print dimensions at selected DPI
- Add text watermark
- Batch resize and export ZIP
- Passport / visa photo size sheet on A4 PDF
- Brightness, contrast and sharpness adjustments
- Inspect image dimensions, format, DPI and metadata basics

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract the ZIP.
3. Double-click `run_windows.bat`.
4. Open the local Streamlit URL shown in the terminal (usually http://localhost:8501).

## Run on Linux
```bash
chmod +x run_linux.sh
./run_linux.sh
```

For OCR on Linux, install Tesseract and Tamil/English language packs if they are not already installed:
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-tam tesseract-ocr-eng
```

## Run manually
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run pdf_studio.py
```

## Deploy to Streamlit Community Cloud
1. Create a new GitHub repository and upload the contents of this project.
2. In Streamlit Community Cloud, select that repository.
3. Set the main file path to `pdf_studio.py`.
4. `packages.txt` installs the system OCR packages during cloud deployment.

## Privacy and limitations
- Image/PDF processing functions are designed to run in the Streamlit app process; uploaded files are held by the active app session and are not intentionally saved to a database.
- Hosting providers may have their own logs, backups, resource limits and retention policies. Do not upload highly confidential documents to a public deployment unless you understand the host's privacy terms.
- Streamlit Community Cloud has memory, execution-time and upload limits. Large PDFs/images may fail on limited instances.
- OCR requires Tesseract language data. Tamil OCR quality depends on scan clarity and available language packs.
- Target KB compression is best-effort. If the requested size cannot be achieved without severe quality loss, the tool reports that.
- Passport/visa photo presets create a print-size layout only. They do not verify official country-specific photo rules, face position, background, or application acceptance. Check the receiving authority's current specifications before submission.
- Find & Replace is a visual PDF text replacement overlay, not a guarantee of perfect font/layout preservation. Review the resulting PDF.
- PDF unlock only works when the correct password is supplied; it does not bypass security.
- No AI background removal, generative enhancement, cloud AI chat, or automatic face recognition is included in this release.

## Project structure
- `pdf_studio.py` — Streamlit user interface
- `pdf_engine.py` — original PDF processing engine
- `image_engine.py` — new image processing engine
- `requirements.txt` — Python dependencies
- `packages.txt` — Linux system packages for OCR
- `run_windows.bat` / `run_linux.sh` — local launch scripts
