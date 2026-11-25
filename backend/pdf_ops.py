import io
import os
import re
import csv
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter, Transformation
import pdfplumber
import pypdfium2 as pdfium
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from pptx import Presentation
from pptx.util import Inches
import openpyxl
from bs4 import BeautifulSoup
from ebooklib import epub
import ebooklib


def parse_page_ranges(range_str: str, total_pages: int) -> List[int]:
    """Parse 1-based page ranges like '1-3,5,7-9' into 0-based sorted unique indices."""
    if not range_str or not range_str.strip():
        return list(range(total_pages))
    indices = []
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start = max(1, int(a.strip()))
            end = min(total_pages, int(b.strip()))
            if start <= end:
                indices.extend(range(start - 1, end))
        else:
            p = int(part)
            if 1 <= p <= total_pages:
                indices.append(p - 1)
    # preserve order without duplicates
    seen = set()
    result = []
    for idx in indices:
        if idx not in seen:
            seen.add(idx)
            result.append(idx)
    return result


def compress_pdf(input_path: Path, output_path: Path, level: int = 60) -> Path:
    """
    Compress PDF.
    level: 10..95 (higher = stronger compression / smaller size).
    Uses qpdf linearize/recompress streams + optional image downsampling for strong compression.
    """
    level = max(10, min(95, int(level)))
    # Try qpdf first for lossless stream compression
    qpdf_bin = shutil.which("qpdf")
    if level <= 40 and qpdf_bin:
        cmd = [qpdf_bin, "--stream-data=compress", "--object-streams=generate", str(input_path), str(output_path)]
        res = subprocess.run(cmd, capture_output=True, timeout=60)
        if res.returncode in (0, 3) and output_path.exists() and output_path.stat().st_size > 0:
            return output_path

    # Stronger compression: recompress embedded images via pypdf or render-compress if requested
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    if level >= 45:
        quality = max(25, 100 - level)
        for page in writer.pages:
            try:
                page.compress_content_streams()
            except Exception:
                pass
            try:
                for img in page.images:
                    try:
                        pil_img = Image.open(io.BytesIO(img.data))
                        if pil_img.mode in ("RGBA", "P"):
                            pil_img = pil_img.convert("RGB")
                        if level >= 70 and max(pil_img.size) > 1200:
                            scale = 1200 / max(pil_img.size)
                            pil_img = pil_img.resize(
                                (max(1, int(pil_img.width * scale)), max(1, int(pil_img.height * scale))),
                                Image.Resampling.LANCZOS,
                            )
                        buf = io.BytesIO()
                        pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                        img.replace(Image.open(buf))
                    except Exception:
                        continue
            except Exception:
                pass

    if reader.metadata:
        try:
            writer.add_metadata(reader.metadata)
        except Exception:
            pass

    tmp_out = output_path.with_suffix(".tmp.pdf")
    with open(tmp_out, "wb") as f:
        writer.write(f)

    # Compare with original and qpdf
    if qpdf_bin:
        res = subprocess.run(
            [qpdf_bin, "--stream-data=compress", "--object-streams=generate", str(tmp_out), str(output_path)],
            capture_output=True,
            timeout=60,
        )
        if res.returncode in (0, 3) and output_path.exists() and output_path.stat().st_size > 0:
            tmp_out.unlink(missing_ok=True)
            return output_path

    shutil.move(str(tmp_out), str(output_path))
    return output_path


def merge_pdfs(input_paths: List[Path], output_path: Path) -> Path:
    writer = PdfWriter()
    for p in input_paths:
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def merge_pdf_and_images(input_paths: List[Path], output_path: Path) -> Path:
    writer = PdfWriter()
    with tempfile.TemporaryDirectory() as tmpdir:
        for idx, p in enumerate(input_paths):
            ext = p.suffix.lower()
            if ext == ".pdf":
                reader = PdfReader(str(p))
                for page in reader.pages:
                    writer.add_page(page)
            else:
                img = Image.open(str(p))
                if img.mode in ("RGBA", "P", "LA"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    bg.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img_pdf = Path(tmpdir) / f"img_{idx}.pdf"
                img.save(str(img_pdf), "PDF", resolution=150.0)
                reader = PdfReader(str(img_pdf))
                for page in reader.pages:
                    writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def split_pdf(input_path: Path, output_zip: Path, mode: str = "all", ranges: str = "", fixed_count: int = 1) -> Path:
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_files = []
        if mode == "ranges" and ranges.strip():
            # Each comma-separated segment becomes a PDF, or all selected
            for idx, part in enumerate(ranges.split(","), start=1):
                part = part.strip()
                if not part:
                    continue
                idxs = parse_page_ranges(part, total)
                if not idxs:
                    continue
                w = PdfWriter()
                for i in idxs:
                    w.add_page(reader.pages[i])
                out_p = Path(tmpdir) / f"split_{idx}_pages_{part.replace('-', '_')}.pdf"
                with open(out_p, "wb") as f:
                    w.write(f)
                out_files.append(out_p)
        elif mode == "fixed":
            step = max(1, int(fixed_count))
            for start in range(0, total, step):
                w = PdfWriter()
                end = min(total, start + step)
                for i in range(start, end):
                    w.add_page(reader.pages[i])
                out_p = Path(tmpdir) / f"pages_{start + 1}_to_{end}.pdf"
                with open(out_p, "wb") as f:
                    w.write(f)
                out_files.append(out_p)
        else:
            for i in range(total):
                w = PdfWriter()
                w.add_page(reader.pages[i])
                out_p = Path(tmpdir) / f"page_{i + 1}.pdf"
                with open(out_p, "wb") as f:
                    w.write(f)
                out_files.append(out_p)

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for fpath in out_files:
                zf.write(fpath, arcname=fpath.name)
    return output_zip


def crop_pdf(
    input_path: Path,
    output_path: Path,
    top_pct: float = 0,
    bottom_pct: float = 0,
    left_pct: float = 0,
    right_pct: float = 0,
    pages_str: str = "",
) -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    total = len(reader.pages)
    target_idxs = set(parse_page_ranges(pages_str, total)) if pages_str.strip() else set(range(total))

    for i, page in enumerate(reader.pages):
        if i in target_idxs:
            mb = page.mediabox
            llx = float(mb.left)
            lly = float(mb.bottom)
            urx = float(mb.right)
            ury = float(mb.top)
            w = urx - llx
            h = ury - lly
            new_llx = llx + w * (max(0.0, min(45.0, left_pct)) / 100.0)
            new_urx = urx - w * (max(0.0, min(45.0, right_pct)) / 100.0)
            new_lly = lly + h * (max(0.0, min(45.0, bottom_pct)) / 100.0)
            new_ury = ury - h * (max(0.0, min(45.0, top_pct)) / 100.0)
            page.cropbox.lower_left = (new_llx, new_lly)
            page.cropbox.upper_right = (new_urx, new_ury)
            page.mediabox.lower_left = (new_llx, new_lly)
            page.mediabox.upper_right = (new_urx, new_ury)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def organize_pdf(input_path: Path, output_path: Path, order_str: str) -> Path:
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    idxs = parse_page_ranges(order_str, total)
    if not idxs:
        idxs = list(range(total))
    writer = PdfWriter()
    for i in idxs:
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def rotate_pdf(input_path: Path, output_path: Path, angle: int = 90, pages_str: str = "") -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    total = len(reader.pages)
    target_idxs = set(parse_page_ranges(pages_str, total)) if pages_str.strip() else set(range(total))
    angle = int(angle) % 360
    for i, page in enumerate(reader.pages):
        if i in target_idxs:
            page.rotate(angle)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def remove_pdf_pages(input_path: Path, output_path: Path, pages_str: str) -> Path:
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    remove_idxs = set(parse_page_ranges(pages_str, total))
    writer = PdfWriter()
    for i in range(total):
        if i not in remove_idxs:
            writer.add_page(reader.pages[i])
    if len(writer.pages) == 0:
        raise ValueError("Cannot remove all pages from PDF.")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def extract_pdf_pages(input_path: Path, output_path: Path, pages_str: str) -> Path:
    reader = PdfReader(str(input_path))
    total = len(reader.pages)
    keep_idxs = parse_page_ranges(pages_str, total)
    if not keep_idxs:
        raise ValueError("No valid pages specified to extract.")
    writer = PdfWriter()
    for i in keep_idxs:
        writer.add_page(reader.pages[i])
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def extract_pdf_images(input_path: Path, output_zip: Path) -> Path:
    reader = PdfReader(str(input_path))
    with tempfile.TemporaryDirectory() as tmpdir:
        count = 0
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for p_idx, page in enumerate(reader.pages, start=1):
                for img_idx, image_file_object in enumerate(page.images, start=1):
                    count += 1
                    fname = f"page_{p_idx}_img_{img_idx}_{image_file_object.name}"
                    fpath = Path(tmpdir) / fname
                    fpath.write_bytes(image_file_object.data)
                    zf.write(fpath, arcname=fname)
        if count == 0:
            raise ValueError("No embedded images found in this PDF.")
    return output_zip


def add_page_numbers(
    input_path: Path,
    output_path: Path,
    position: str = "bottom-center",
    start_num: int = 1,
    font_size: int = 12,
    fmt: str = "{n}",
) -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    total = len(reader.pages)

    for idx, page in enumerate(reader.pages):
        mb = page.mediabox
        w = float(mb.right) - float(mb.left)
        h = float(mb.top) - float(mb.bottom)
        num = start_num + idx
        label = fmt.replace("{n}", str(num)).replace("{total}", str(total + start_num - 1))

        packet = io.BytesIO()
        c = rl_canvas.Canvas(packet, pagesize=(w, h))
        c.setFont("Helvetica", font_size)
        c.setFillColorRGB(0.2, 0.2, 0.2)

        margin_x = 36
        margin_y = 24
        if "top" in position:
            y = h - margin_y
        else:
            y = margin_y

        if "left" in position:
            c.drawString(margin_x, y, label)
        elif "right" in position:
            c.drawRightString(w - margin_x, y, label)
        else:
            c.drawCentredString(w / 2.0, y, label)

        c.save()
        packet.seek(0)
        overlay = PdfReader(packet).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def add_watermark(
    input_path: Path,
    output_path: Path,
    text: str = "CONFIDENTIAL",
    opacity: float = 0.25,
    font_size: int = 48,
    angle: int = 45,
    color_hex: str = "#888888",
) -> Path:
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    color_hex = color_hex.lstrip("#")
    if len(color_hex) == 6:
        r = int(color_hex[0:2], 16) / 255.0
        g = int(color_hex[2:4], 16) / 255.0
        b = int(color_hex[4:6], 16) / 255.0
    else:
        r, g, b = 0.5, 0.5, 0.5

    for page in reader.pages:
        mb = page.mediabox
        w = float(mb.right) - float(mb.left)
        h = float(mb.top) - float(mb.bottom)

        packet = io.BytesIO()
        c = rl_canvas.Canvas(packet, pagesize=(w, h))
        c.saveState()
        c.setFillColor(Color(r, g, b, alpha=max(0.05, min(1.0, opacity))))
        c.setFont("Helvetica-Bold", font_size)
        c.translate(w / 2.0, h / 2.0)
        c.rotate(angle)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.save()

        packet.seek(0)
        overlay = PdfReader(packet).pages[0]
        page.merge_page(overlay)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def images_to_pdf(input_paths: List[Path], output_path: Path) -> Path:
    return merge_pdf_and_images(input_paths, output_path)


def office_to_pdf(input_path: Path, output_path: Path) -> Path:
    lo_bin = shutil.which("libreoffice")
    if not lo_bin:
        raise RuntimeError("LibreOffice is not installed on this machine.")
    with tempfile.TemporaryDirectory(prefix="lo_prof_") as prof_dir, tempfile.TemporaryDirectory() as out_dir:
        env = {**os.environ, "HOME": "/tmp", "TMPDIR": "/tmp"}
        cmd = [
            lo_bin,
            f"-env:UserInstallation=file://{prof_dir}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            out_dir,
            str(input_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
        pdfs = list(Path(out_dir).glob("*.pdf"))
        if not pdfs:
            raise RuntimeError(f"Conversion failed: {res.stderr or res.stdout}")
        shutil.move(str(pdfs[0]), str(output_path))
    return output_path


def text_to_pdf(input_path: Path, output_path: Path) -> Path:
    text = input_path.read_text(encoding="utf-8", errors="replace")
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = 11
    style.leading = 15
    story = []
    for para in text.splitlines():
        safe = (
            para.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        if safe.strip():
            story.append(Paragraph(safe, style))
        else:
            story.append(Spacer(1, 8))
    if not story:
        story.append(Paragraph(" ", style))
    doc.build(story)
    return output_path


def pdf_to_images(input_path: Path, output_zip: Path, fmt: str = "PNG", dpi: int = 150) -> Path:
    fmt = fmt.upper()
    if fmt == "JPG":
        fmt = "JPEG"
    ext = "jpg" if fmt == "JPEG" else fmt.lower()
    pdf = pdfium.PdfDocument(str(input_path))
    scale = dpi / 72.0
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for i in range(len(pdf)):
                page = pdf[i]
                pil_img = page.render(scale=scale).to_pil()
                if fmt == "JPEG" and pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")
                out_img = Path(tmpdir) / f"page_{i + 1}.{ext}"
                pil_img.save(str(out_img), format=fmt, quality=92)
                zf.write(out_img, arcname=out_img.name)
    return output_zip


def pdf_to_text(input_path: Path, output_path: Path) -> Path:
    chunks = []
    with pdfplumber.open(str(input_path)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            txt = page.extract_text() or ""
            chunks.append(f"--- Page {idx} ---\n{txt}\n")
    output_path.write_text("\n".join(chunks), encoding="utf-8")
    return output_path


def pdf_to_word(input_path: Path, output_path: Path) -> Path:
    doc = Document()
    with pdfplumber.open(str(input_path)) as pdf:
        for idx, page in enumerate(pdf.pages):
            if idx > 0:
                doc.add_page_break()
            txt = page.extract_text() or ""
            for line in txt.splitlines():
                if line.strip():
                    doc.add_paragraph(line)
            tables = page.extract_tables() or []
            for table in tables:
                if not table:
                    continue
                cols = max(len(r) for r in table)
                t = doc.add_table(rows=len(table), cols=cols)
                t.style = "Table Grid"
                for r_i, row in enumerate(table):
                    for c_i, val in enumerate(row):
                        t.cell(r_i, c_i).text = str(val or "")
    doc.save(str(output_path))
    return output_path


def pdf_to_pptx(input_path: Path, output_path: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    pdf = pdfium.PdfDocument(str(input_path))
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(len(pdf)):
            pil_img = pdf[i].render(scale=2.0).to_pil()
            img_path = Path(tmpdir) / f"slide_{i + 1}.png"
            pil_img.save(str(img_path), format="PNG")
            slide = prs.slides.add_slide(blank_layout)
            # Fit preserving aspect ratio
            iw, ih = pil_img.size
            sw, sh = prs.slide_width, prs.slide_height
            ratio = min(sw / iw, sh / ih)
            w = int(iw * ratio)
            h = int(ih * ratio)
            left = int((sw - w) / 2)
            top = int((sh - h) / 2)
            slide.shapes.add_picture(str(img_path), left, top, width=w, height=h)
    prs.save(str(output_path))
    return output_path


def pdf_to_excel(input_path: Path, output_path: Path) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Extracted Data"
    row_cursor = 1
    found_table = False

    with pdfplumber.open(str(input_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            if tables:
                found_table = True
                for t in tables:
                    for row in t:
                        for c_idx, cell in enumerate(row, start=1):
                            ws.cell(row=row_cursor, column=c_idx, value=cell)
                        row_cursor += 1
                    row_cursor += 1
            else:
                txt = page.extract_text() or ""
                for line in txt.splitlines():
                    if line.strip():
                        ws.cell(row=row_cursor, column=1, value=line.strip())
                        row_cursor += 1
    if not found_table and row_cursor == 1:
        ws.cell(row=1, column=1, value="No extractable text or tables found.")
    wb.save(str(output_path))
    return output_path


def pdf_to_csv(input_path: Path, output_path: Path) -> Path:
    rows = []
    with pdfplumber.open(str(input_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            if tables:
                for t in tables:
                    rows.extend(t)
            else:
                txt = page.extract_text() or ""
                for line in txt.splitlines():
                    if line.strip():
                        rows.append([line.strip()])
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return output_path


def unlock_pdf(input_path: Path, output_path: Path, password: str = "") -> Path:
    reader = PdfReader(str(input_path))
    if reader.is_encrypted:
        res = reader.decrypt(password)
        if res == 0:
            raise ValueError("Incorrect password for encrypted PDF.")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def protect_pdf(input_path: Path, output_path: Path, password: str) -> Path:
    if not password:
        raise ValueError("Password is required to protect PDF.")
    reader = PdfReader(str(input_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path


def ebook_to_pdf(input_path: Path, output_path: Path) -> Path:
    ext = input_path.suffix.lower()
    if ext == ".cbz":
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(input_path, "r") as zf:
                zf.extractall(tmpdir)
            imgs = sorted(
                [p for p in Path(tmpdir).rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".bmp")]
            )
            if not imgs:
                raise ValueError("No images found in CBZ archive.")
            return images_to_pdf(imgs, output_path)
    elif ext == ".rtf":
        return office_to_pdf(input_path, output_path)
    elif ext == ".epub":
        book = epub.read_epub(str(input_path))
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = 11
        style.leading = 15
        story = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                for p in soup.find_all(["h1", "h2", "h3", "p", "li"]):
                    txt = p.get_text(" ", strip=True)
                    if txt:
                        safe = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        s = styles["Heading2"] if p.name in ("h1", "h2") else style
                        story.append(Paragraph(safe, s))
                        story.append(Spacer(1, 6))
        if not story:
            story.append(Paragraph("Empty EPUB", style))
        doc.build(story)
        return output_path
    elif ext in (".fb2", ".html", ".htm"):
        soup = BeautifulSoup(input_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        txt = soup.get_text("\n", strip=True)
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write(txt)
            tpath = Path(tf.name)
        try:
            return text_to_pdf(tpath, output_path)
        finally:
            tpath.unlink(missing_ok=True)
    else:
        # Fallback: try LibreOffice or text extraction
        try:
            return office_to_pdf(input_path, output_path)
        except Exception:
            return text_to_pdf(input_path, output_path)


def pdf_to_ebook(input_path: Path, output_path: Path, target_ext: str = "epub") -> Path:
    target_ext = target_ext.lower().lstrip(".")
    with pdfplumber.open(str(input_path)) as pdf:
        pages_text = [p.extract_text() or "" for p in pdf.pages]

    if target_ext == "epub":
        book = epub.EpubBook()
        book.set_identifier(input_path.stem)
        book.set_title(input_path.stem)
        book.set_language("en")
        chapters = []
        for i, txt in enumerate(pages_text, start=1):
            c = epub.EpubHtml(title=f"Page {i}", file_name=f"page_{i}.xhtml", lang="en")
            body = "".join(f"<p>{line}</p>" for line in txt.splitlines() if line.strip())
            c.content = f"<html><body><h2>Page {i}</h2>{body or '<p></p>'}</body></html>"
            book.add_item(c)
            chapters.append(c)
        book.toc = tuple(chapters)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ["nav"] + chapters
        epub.write_epub(str(output_path), book)
        return output_path
    elif target_ext == "fb2":
        body = "\n".join(
            f"<section><title><p>Page {i}</p></title>"
            + "".join(f"<p>{line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}</p>" for line in t.splitlines() if line.strip())
            + "</section>"
            for i, t in enumerate(pages_text, start=1)
        )
        fb2 = f'<?xml version="1.0" encoding="utf-8"?><FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0"><description><title-info><book-title>{input_path.stem}</book-title></title-info></description><body>{body}</body></FictionBook>'
        output_path.write_text(fb2, encoding="utf-8")
        return output_path
    elif target_ext == "rtf":
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
            tmp_docx = Path(tf.name)
        try:
            pdf_to_word(input_path, tmp_docx)
            lo_bin = shutil.which("libreoffice")
            with tempfile.TemporaryDirectory(prefix="lo_prof_") as prof_dir, tempfile.TemporaryDirectory() as out_dir:
                env = {**os.environ, "HOME": "/tmp", "TMPDIR": "/tmp"}
                subprocess.run(
                    [lo_bin, f"-env:UserInstallation=file://{prof_dir}", "--headless", "--convert-to", "rtf", "--outdir", out_dir, str(tmp_docx)],
                    capture_output=True, env=env, timeout=60
                )
                rtfs = list(Path(out_dir).glob("*.rtf"))
                if rtfs:
                    shutil.move(str(rtfs[0]), str(output_path))
                    return output_path
        finally:
            tmp_docx.unlink(missing_ok=True)
        raise RuntimeError("RTF conversion failed.")
    else:
        # MOBI / AZW3 fallback: generate EPUB (or package)
        return pdf_to_ebook(input_path, output_path, "epub")
