import io
import re
import zipfile
import fitz  # PyMuPDF
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import pdfplumber
import pandas as pd
from docx import Document


def parse_page_ranges(range_str: str, max_pages: int, preserve_order: bool = False):
    """Parse strings like '1, 3, 5-8' into 0-based page indices."""
    pages = [] if preserve_order else set()
    for part in range_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                step = 1 if start <= end else -1
                for p in range(start, end + step, step):
                    if 1 <= p <= max_pages:
                        idx = p - 1
                        if preserve_order:
                            pages.append(idx)
                        else:
                            pages.add(idx)
            except ValueError:
                continue
        elif part.isdigit():
            p = int(part)
            if 1 <= p <= max_pages:
                idx = p - 1
                if preserve_order:
                    pages.append(idx)
                else:
                    pages.add(idx)
    return pages if preserve_order else sorted(list(pages))


def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
    merged = fitz.open()
    for b in pdf_bytes_list:
        with fitz.open(stream=b, filetype="pdf") as doc:
            merged.insert_pdf(doc)
    buf = io.BytesIO()
    merged.save(buf, garbage=4, deflate=True)
    merged.close()
    return buf.getvalue()


def extract_pages(pdf_bytes: bytes, page_indices: list[int]) -> bytes:
    new_doc = fitz.open()
    with fitz.open(stream=pdf_bytes, filetype="pdf") as src:
        for idx in page_indices:
            new_doc.insert_pdf(src, from_page=idx, to_page=idx)
    buf = io.BytesIO()
    new_doc.save(buf, garbage=4, deflate=True)
    new_doc.close()
    return buf.getvalue()


def transform_pages(
    pdf_bytes: bytes,
    ordered_indices: list[int],
    rotate_angle: int = 0,
    rotate_targets: set[int] | None = None,
) -> bytes:
    new_doc = fitz.open()
    with fitz.open(stream=pdf_bytes, filetype="pdf") as src:
        total = len(src)
        targets = rotate_targets if rotate_targets is not None else set(range(total))
        for orig_idx in ordered_indices:
            new_doc.insert_pdf(src, from_page=orig_idx, to_page=orig_idx)
            if rotate_angle % 360 != 0 and orig_idx in targets:
                page = new_doc[-1]
                page.set_rotation((page.rotation + rotate_angle) % 360)
    buf = io.BytesIO()
    new_doc.save(buf, garbage=4, deflate=True)
    new_doc.close()
    return buf.getvalue()


def crop_pdf(
    pdf_bytes: bytes,
    left_pct: float,
    right_pct: float,
    top_pct: float,
    bottom_pct: float,
    preview_only: bool = False,
):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        r = page.rect
        rect = fitz.Rect(
            r.x0 + (left_pct / 100.0) * r.width,
            r.y0 + (top_pct / 100.0) * r.height,
            r.x1 - (right_pct / 100.0) * r.width,
            r.y1 - (bottom_pct / 100.0) * r.height,
        )
        page.set_cropbox(rect)
        if preview_only:
            break
    if preview_only:
        png = doc[0].get_pixmap(dpi=110).tobytes("png")
        doc.close()
        return png
    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    return buf.getvalue()


def _compress_once(pdf_bytes: bytes, dpi: int, quality: int) -> bytes:
    out_doc = fitz.open()
    with fitz.open(stream=pdf_bytes, filetype="pdf") as src:
        for page in src:
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_buf = io.BytesIO()
            img.save(img_buf, format="JPEG", quality=quality, optimize=True)
            new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(page.rect, stream=img_buf.getvalue())
    buf = io.BytesIO()
    out_doc.save(buf, garbage=4, deflate=True)
    out_doc.close()
    return buf.getvalue()


def compress_pdf_smart(
    pdf_bytes: bytes,
    dpi: int = 110,
    quality: int = 65,
    target_kb: float | None = None,
) -> bytes:
    if not target_kb or target_kb <= 0:
        return _compress_once(pdf_bytes, dpi=dpi, quality=quality)

    # Smart step-down search toward target_kb without dropping below safe minimums
    candidate_configs = [
        (140, 75),
        (115, 65),
        (95, 55),
        (80, 45),
        (65, 35),
        (55, 28),
    ]
    best_bytes = None
    for d, q in candidate_configs:
        data = _compress_once(pdf_bytes, dpi=d, quality=q)
        best_bytes = data
        if (len(data) / 1024.0) <= target_kb:
            return data
    return best_bytes


def add_stamp_to_page(
    pdf_bytes: bytes,
    stamp_bytes: bytes,
    page_num_1based: int,
    x_pct: float,
    y_pct: float,
    width_px: float,
    preview_only: bool = False,
) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_num_1based - 1]
    w, h = page.rect.width, page.rect.height
    x0 = (x_pct / 100.0) * w
    y0 = (y_pct / 100.0) * h
    pil_stamp = Image.open(io.BytesIO(stamp_bytes))
    aspect = pil_stamp.height / max(1, pil_stamp.width)
    rect = fitz.Rect(x0, y0, x0 + width_px, y0 + (width_px * aspect))
    page.insert_image(rect, stream=stamp_bytes)

    if preview_only:
        png = page.get_pixmap(dpi=110).tobytes("png")
        doc.close()
        return png

    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    return buf.getvalue()


def apply_watermark_and_pageno(
    pdf_bytes: bytes,
    add_wm: bool = True,
    wm_text: str = "COPY ONLY",
    wm_opacity: float = 0.20,
    wm_fontsize: int = 52,
    wm_color: tuple[float, float, float] = (0.5, 0.5, 0.5),
    add_pageno: bool = True,
    pno_prefix: str = "Page",
    pno_pos: str = "Bottom Center",
) -> bytes:
    out_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total = len(out_doc)
    font = fitz.Font("helv")

    for idx, page in enumerate(out_doc):
        w, h = page.rect.width, page.rect.height
        if add_wm and wm_text.strip():
            tw = fitz.get_text_length(wm_text, fontname="helv", fontsize=wm_fontsize)
            center_pt = fitz.Point(w / 2 - tw / 3, h / 2 + wm_fontsize / 3)
            writer = fitz.TextWriter(page.rect, opacity=wm_opacity)
            writer.append(center_pt, wm_text, font=font, fontsize=wm_fontsize)
            writer.write_text(page, color=wm_color, morph=(fitz.Point(w / 2, h / 2), fitz.Matrix(-45)))

        if add_pageno:
            label = f"{pno_prefix} {idx + 1} of {total}".strip()
            lw = fitz.get_text_length(label, fontname="helv", fontsize=11)
            pos_map = {
                "Bottom Center": fitz.Point((w - lw) / 2, h - 22),
                "Bottom Right": fitz.Point(w - lw - 28, h - 22),
                "Bottom Left": fitz.Point(28, h - 22),
                "Top Right": fitz.Point(w - lw - 28, 28),
                "Top Center": fitz.Point((w - lw) / 2, 28),
                "Top Left": fitz.Point(28, 28),
            }
            page.insert_text(pos_map.get(pno_pos, pos_map["Bottom Center"]), label, fontname="helv", fontsize=11, color=(0.25, 0.25, 0.25))

    buf = io.BytesIO()
    out_doc.save(buf, garbage=4, deflate=True)
    out_doc.close()
    return buf.getvalue()


def images_to_pdf(image_items: list[tuple[str, bytes]]) -> bytes:
    pdf_doc = fitz.open()
    for filename, img_bytes in image_items:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
        img_doc = fitz.open(stream=img_bytes, filetype=ext)
        rect = img_doc[0].rect
        img_pdf = fitz.open("pdf", img_doc.convert_to_pdf())
        page = pdf_doc.new_page(width=rect.width, height=rect.height)
        page.show_pdf_page(rect, img_pdf, 0)
        img_pdf.close()
        img_doc.close()
    buf = io.BytesIO()
    pdf_doc.save(buf, garbage=4, deflate=True)
    pdf_doc.close()
    return buf.getvalue()


def pdf_to_images(pdf_bytes: bytes, page_indices: list[int], fmt: str = "PNG", dpi: int = 200) -> list[tuple[str, bytes]]:
    results = []
    ext = fmt.lower()
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for idx in page_indices:
            pix = doc[idx].get_pixmap(dpi=dpi)
            if fmt.upper() == "PNG":
                img_bytes = pix.tobytes("png")
            else:
                pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                b = io.BytesIO()
                pil_img.save(b, format="JPEG", quality=92, optimize=True)
                img_bytes = b.getvalue()
            results.append((f"page_{idx + 1}.{ext}", img_bytes))
    return results


def _preprocess_for_ocr(img: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(img)
    return ImageEnhance.Contrast(gray).enhance(1.35)


def extract_text_ocr(
    file_bytes: bytes,
    is_pdf: bool,
    lang: str = "tam+eng",
    force_ocr: bool = False,
    dpi: int = 350,
    enhance_img: bool = True,
) -> str:
    parts = []
    if is_pdf:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for idx, page in enumerate(doc):
                direct = "" if force_ocr else page.get_text("text").strip()
                if len(direct) > 20:
                    parts.append(f"--- Page {idx + 1} ---\n{direct}")
                else:
                    pix = page.get_pixmap(dpi=dpi)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    if enhance_img:
                        img = _preprocess_for_ocr(img)
                    txt = pytesseract.image_to_string(img, lang=lang, config="--psm 6").strip()
                    parts.append(f"--- Page {idx + 1} (OCR) ---\n{txt}")
    else:
        img = Image.open(io.BytesIO(file_bytes))
        if enhance_img:
            img = _preprocess_for_ocr(img)
        txt = pytesseract.image_to_string(img, lang=lang, config="--psm 6").strip()
        parts.append(txt)
    return "\n\n".join(parts)


def pdf_to_docx_and_txt(pdf_bytes: bytes, ocr_fallback: bool = True, lang: str = "tam+eng") -> tuple[bytes, str]:
    word_doc = Document()
    txt_parts = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        total = len(doc)
        for idx, page in enumerate(doc):
            txt = page.get_text("text").strip()
            if len(txt) < 20 and ocr_fallback:
                pix = page.get_pixmap(dpi=300)
                img = _preprocess_for_ocr(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
                txt = pytesseract.image_to_string(img, lang=lang, config="--psm 6").strip()
            word_doc.add_heading(f"Page {idx + 1}", level=2)
            for line in txt.splitlines():
                if line.strip():
                    word_doc.add_paragraph(line.strip())
            if idx < total - 1:
                word_doc.add_page_break()
            txt_parts.append(f"--- Page {idx + 1} ---\n{txt}")

    buf = io.BytesIO()
    word_doc.save(buf)
    return buf.getvalue(), "\n\n".join(txt_parts)


def extract_tables_to_excel(pdf_bytes: bytes) -> tuple[list[tuple[str, pd.DataFrame]], bytes | None]:
    tables_found = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            for t_idx, table in enumerate(page.extract_tables()):
                if table and len(table) > 1:
                    cols = [c if c else f"Col_{i + 1}" for i, c in enumerate(table[0])]
                    df = pd.DataFrame(table[1:], columns=cols)
                    tables_found.append((f"Page_{p_idx + 1}Table{t_idx + 1}", df))

    if not tables_found:
        return [], None

    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        for sheet_name, df in tables_found:
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return tables_found, excel_buf.getvalue()


def highlight_terms(pdf_bytes: bytes, terms: list[str]) -> tuple[bytes | None, int]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    hits = 0
    for page in doc:
        for t in terms:
            for rect in page.search_for(t):
                page.add_highlight_annot(rect)
                hits += 1
    if hits == 0:
        doc.close()
        return None, 0
    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    return buf.getvalue(), hits


def find_and_replace_overlay(pdf_bytes: bytes, find_str: str, replace_str: str, fontsize: int = 11) -> tuple[bytes | None, int]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    count = 0
    for page in doc:
        rects = page.search_for(find_str)
        if not rects:
            continue
        for r in rects:
            page.add_redact_annot(r, fill=(1, 1, 1))
            count += 1
        page.apply_redactions()
        for r in rects:
            page.insert_text(fitz.Point(r.x0, r.y1 - 2), replace_str, fontname="helv", fontsize=fontsize, color=(0, 0, 0))
    if count == 0:
        doc.close()
        return None, 0
    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    return buf.getvalue(), count


def smart_redact(
    pdf_bytes: bytes,
    custom_terms: list[str],
    auto_phone: bool = True,
    auto_aadhaar12: bool = True,
    auto_email: bool = False,
    fill_color: tuple[float, float, float] = (0, 0, 0),
) -> tuple[bytes | None, int]:
    patterns = []
    if auto_phone:
        patterns.append(r"\b[6-9]\d{9}\b")
    if auto_aadhaar12:
        patterns.append(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
    if auto_email:
        patterns.append(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_redactions = 0

    for page in doc:
        targets = list(custom_terms)
        if patterns:
            text = page.get_text("text")
            for pat in patterns:
                for found in re.findall(pat, text):
                    clean = found.strip()
                    if clean and clean not in targets:
                        targets.append(clean)

        for target in targets:
            for rect in page.search_for(target):
                page.add_redact_annot(rect, fill=fill_color)
                total_redactions += 1
        page.apply_redactions()

    if total_redactions == 0:
        doc.close()
        return None, 0

    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    return buf.getvalue(), total_redactions


def inspect_and_clean_metadata(pdf_bytes: bytes, clean: bool = False) -> tuple[dict, bytes | None]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    meta = dict(doc.metadata or {})
    if not clean:
        doc.close()
        return meta, None

    doc.set_metadata({})
    try:
        doc.del_xml_metadata()
    except Exception:
        pass
    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True)
    doc.close()
    return meta, buf.getvalue()


def lock_or_unlock_pdf(
    pdf_bytes: bytes,
    lock: bool,
    user_pw: str = "",
    owner_pw: str = "",
    allow_print: bool = True,
) -> tuple[bool, str, bytes | None]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if lock:
        if not user_pw:
            doc.close()
            return False, "⚠️ பாஸ்வேர்ட் உள்ளிடவும்!", None
        perms = fitz.PDF_PERM_PRINT if allow_print else 0
        buf = io.BytesIO()
        doc.save(
            buf,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=user_pw,
            owner_pw=owner_pw if owner_pw else f"{user_pw}_owner",
            permissions=perms,
        )
        doc.close()
        return True, "✅ PDF AES-256 பாதுகாப்புடன் பூட்டப்பட்டுவிட்டது!", buf.getvalue()

    if doc.needs_pass and not doc.authenticate(user_pw):
        doc.close()
        return False, "❌ பாஸ்வேர்ட் தவறானது!", None
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return True, "✅ PDF பாஸ்வேர்ட் நீக்கப்பட்டுவிட்டது!", buf.getvalue()


def impose_a4_sheet(pdf_items: list[tuple[str, bytes]], mode: str = "2-Up", add_border: bool = True) -> tuple[bytes, int]:
    opened_docs = []
    pages_ref = []
    for _, b in pdf_items:
        d = fitz.open(stream=b, filetype="pdf")
        opened_docs.append(d)
        for i in range(len(d)):
            pages_ref.append((d, i))

    out_doc = fitz.open()
    a4_w, a4_h = 595, 842
    margin = 20

    if mode.startswith("2-Up"):
        slots = [
            fitz.Rect(margin, margin, a4_w - margin, a4_h / 2 - margin / 2),
            fitz.Rect(margin, a4_h / 2 + margin / 2, a4_w - margin, a4_h - margin),
        ]
    else:
        slots = [
            fitz.Rect(margin, margin, a4_w / 2 - margin / 2, a4_h / 2 - margin / 2),
            fitz.Rect(a4_w / 2 + margin / 2, margin, a4_w - margin, a4_h / 2 - margin / 2),
            fitz.Rect(margin, a4_h / 2 + margin / 2, a4_w / 2 - margin / 2, a4_h - margin),
            fitz.Rect(a4_w / 2 + margin / 2, a4_h / 2 + margin / 2, a4_w - margin, a4_h - margin),
        ]

    per_sheet = len(slots)
    for start in range(0, len(pages_ref), per_sheet):
        sheet = out_doc.new_page(width=a4_w, height=a4_h)
        for j in range(per_sheet):
            if start + j < len(pages_ref):
                src_d, p_idx = pages_ref[start + j]
                sheet.show_pdf_page(slots[j], src_d, p_idx)
                if add_border:
                    sheet.draw_rect(slots[j], color=(0.75, 0.75, 0.75), width=0.6)

    sheet_count = len(out_doc)
    buf = io.BytesIO()
    out_doc.save(buf, garbage=4, deflate=True)
    out_doc.close()
    for d in opened_docs:
        d.close()
    return buf.getvalue(), sheet_count


def extract_embedded_images(pdf_bytes: bytes) -> list[tuple[str, bytes]]:
    extracted = []
    seen = set()
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for p_idx, page in enumerate(doc):
            for img_idx, info in enumerate(page.get_images(full=True)):
                xref = info[0]
                if xref in seen:
                    continue
                seen.add(xref)
                base = doc.extract_image(xref)
                extracted.append((f"Page_{p_idx + 1}Img{img_idx + 1}.{base['ext']}", base["image"]))
    return extracted


def build_zip(files: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files:
            zf.writestr(fname, content)
    return buf.getvalue()