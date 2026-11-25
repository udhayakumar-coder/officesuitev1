# BIGPDF 11zon — Localhost Full-Stack Clone

A complete, offline, privacy-first localhost clone of **bigpdf.11zon.com** built with **FastAPI (Python)** + **Vanilla HTML/CSS/JS**.

## Features Included
- **Optimize & Merge PDF**: Compress PDF (slider), Merge PDF, Merge PDF & Image, Split PDF (all/ranges/fixed).
- **View & Edit PDF**: Crop PDF Page, Organize PDF, Rotate PDF, Remove Pages, Extract Pages, Extract Images, Add Page Number, Add Watermark.
- **Convert To PDF**: Image/JPG/PNG/AVIF/HEIC/TIFF/JFIF to PDF, Word/DOC/DOCX/DOCM/ODT/RTF to PDF, PowerPoint/PPT/PPTX/PPSX/ODP to PDF, Excel/XLS/XLSX/ODS/CSV to PDF, Text to PDF.
- **Convert From PDF**: PDF to Image/JPG, PDF to Word, PDF to PowerPoint, PDF to Excel, PDF to Text, PDF to CSV.
- **PDF Security**: Unlock PDF, Protect PDF.
- **eBook Converter**: EPUB/FB2/CBZ/RTF to PDF, PDF to EPUB/FB2/RTF.
- **Image Tools**: Compress Image (JPG/PNG/WEBP/BMP), Convert Image (JPG/PNG/WEBP/JPEG), Crop, Resize, Rotate, Crop Circle, Merge Photo, Photo & Signature Resize (with KB target).
- **GIF, ZIP & Utilities**: Images to GIF, GIF to Images, ZIP Maker, ZIP Extractor, Barcode Generator (Code 128), Password Generator, Color Extractor.

## Setup & Run on Localhost

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Optional for Word/Excel/PowerPoint -> PDF conversion: install **LibreOffice** on your system.)*

2. **Start the server**:
   - **Windows**: Double-click `run.bat` or run:
     ```cmd
     python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
     ```
   - **Linux / macOS**:
     ```bash
     chmod +x run.sh
     ./run.sh
     ```

3. **Open in browser**:
   Visit **http://127.0.0.1:8000**
