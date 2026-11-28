import streamlit as st
import fitz
import pdf_engine as eng

st.set_page_config(
    page_title="Pro PDF Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    :root {
        color-scheme: light;
    }

    /* Main Light Pink Background & Black Letters */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background-color: #93c47d !important;
        background: linear-gradient(180deg, #f1c232 0%, #7fb1df 100%) !important;
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Tamil", sans-serif;
    }

    /* All General Text Black */
    p, span, label, h1, h2, h3, h4, h5, h6, div, li, .stMarkdown {
        color: #000000 !important;
    }

    /* Sidebar Soft Blush Pink + Gold Border */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        background-color: #FFEBF2 !important;
        background: #FFEBF2 !important;
        color: #000000 !important;
        border-right: 2px solid #D4AF37 !important;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* Hero Card with Gold & Light Red Accent */
    .studio-hero {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF7FA 65%, #FFFBEB 100%) !important;
        border: 1.5px solid #E5C158 !important;
        border-left: 7px solid #E11D48 !important;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 3px 10px rgba(212, 175, 55, 0.14);
    }

    /* Gold Shade Badge */
    .studio-badge {
        display: inline-block;
        background: linear-gradient(90deg, #FEF3C7 0%, #FDE68A 100%) !important;
        color: #111111 !important;
        border: 1px solid #D4AF37 !important;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 8px;
    }

    .studio-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #000000 !important;
        margin: 0 0 6px 0;
    }

    .studio-subtitle {
        font-size: 0.95rem;
        color: #1A1A1A !important;
        margin: 0;
    }

    /* Light Red Shade on Icons / Material Icons / SVG Icons */
    [data-testid="stIconMaterial"],
    .stIconMaterial,
    svg {
        color: #F43F5E !important;
    }
    /* Keep download/upload/button icons crisp */
    button svg {
        color: #FFFFFF !important;
    }

    /* Input Boxes & Upload Dropzone */
    input, textarea,
    [data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #F9A8D4 !important;
        border-radius: 9px !important;
    }
    input::placeholder, textarea::placeholder {
        color: #4B5563 !important;
    }

    /* Primary Button: Light Red / Rose with Gold Border */
    .stButton > button {
        background-color: #E11D48 !important;
        color: #FFFFFF !important;
        border: 1.5px solid #D4AF37 !important;
        border-radius: 9px !important;
        padding: 0.52rem 1.25rem !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background-color: #BE123C !important;
    }

    /* Download Button: Gold Shade with Dark/Crisp Contrast */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%) !important;
        color: #000000 !important;
        border: 1.5px solid #9A7B2C !important;
        border-radius: 9px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 700 !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #E5C158 0%, #C59B27 100%) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="studio-hero">
        <div class="studio-badge">⚡ 21-IN-1 COMPLETE ENGINE • FAST &amp; CLEAN UI</div>
        <div class="studio-title">📄 Pro PDF Studio</div>
        <div class="studio-subtitle">
            Merge • Split • Rotate/Reorder • Crop • Compress • Stamp • Watermark • OCR (தமிழ் + Eng) • Word • Excel • Redact • Lock/Unlock
        </div>
    </div>
""", unsafe_allow_html=True)

ALL_TOOLS = [
    "1. 🔗 Merge PDFs (இணைக்க)",
    "2. ✂️ Split / Extract (பிரிக்க)",
    "3. 🔄 Rotate, Reorder & Delete",
    "4. 📐 Crop Pages (வெட்ட)",
    "5. 🖋️ Add Stamp / Sign (சீல்)",
    "6. 💧 Watermark & Page Numbers",
    "7. 🔐 Lock PDF (பாஸ்வேர்ட் போட)",
    "8. 🔓 Unlock PDF (பாஸ்வேர்ட் நீக்க)",
    "9. 🛡️ Smart Redact (தகவல் மறைப்பு)",
    "10. 🧹 Metadata Cleaner",
    "11. 🗜️ Smart Compress (Target KB)",
    "12. 📦 Batch Compress (பல ஃபைல்கள்)",
    "13. 💦 Batch Watermark (பல ஃபைல்கள்)",
    "14. 🪪 A4 Sheet Imposition (2-Up / 4-Up)",
    "15. 🖼️ Extract Embedded Images",
    "16. 🖼️ Images to PDF (படங்களை மாற்ற)",
    "17. 📸 PDF to Images (JPG / PNG)",
    "18. 🔍 OCR Text Extract (தமிழ் + Eng)",
    "19. 📝 PDF to Word (.docx)",
    "20. 📊 PDF Table to Excel (.xlsx)",
    "21. 🖍️ Search & Highlight / Replace",
    "22. Image Studio (Resize / Compress / Convert / Print)"
]

with st.sidebar:
    st.markdown("### 🛠️ All 21 PDF Tools")
    tool = st.radio("கருவியைத் தேர்ந்தெடுக்கவும்:", ALL_TOOLS)
    st.divider()
    st.caption("🔒 *100% Privacy:* உங்கள் ஃபைல்கள் பாதுகாப்பாகச் செயலாக்கப்படுகின்றன.")

if tool == "1. 🔗 Merge PDFs (இணைக்க)":
    st.subheader("🔗 பல PDF ஃபைல்களை ஒன்றாக இணைக்க")
    files = st.file_uploader("PDF ஃபைல்கள்", type=["pdf"], accept_multiple_files=True, key="t1")
    out_name = st.text_input("Output File Name", "Merged_Output.pdf", key="t1_n")
    if files and st.button("Run Merge", key="b1"):
        res = eng.merge_pdfs([f.read() for f in files])
        st.download_button("⬇️ Download Merged PDF", res, out_name if out_name.endswith(".pdf") else f"{out_name}.pdf", "application/pdf")

elif tool == "2. ✂️ Split / Extract (பிரிக்க)":
    st.subheader("✂️ தேவையான பக்கங்களை மட்டும் பிரித்தெடுக்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t2")
    if f:
        raw = f.read()
        with fitz.open(stream=raw, filetype="pdf") as d:
            total = len(d)
        st.info(f"மொத்தப் பக்கங்கள்: *{total}*")
        rng = st.text_input("Pages (உதா: 1, 3, 5-8)", "1", key="t2_r")
        if st.button("Extract Pages", key="b2"):
            idxs = eng.parse_page_ranges(rng, total)
            if not idxs:
                st.error("⚠️ சரியான பக்க எண்களை உள்ளிடவும்.")
            else:
                st.download_button("⬇️ Download Extracted PDF", eng.extract_pages(raw, idxs), f"Extracted_{f.name}", "application/pdf")

elif tool == "3. 🔄 Rotate, Reorder & Delete":
    st.subheader("🔄 பக்கங்களைத் திருப்ப, வரிசை மாற்ற அல்லது நீக்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t3")
    if f:
        raw = f.read()
        with fitz.open(stream=raw, filetype="pdf") as d:
            total = len(d)
        st.info(f"மொத்தப் பக்கங்கள்: *{total}*")
        order_s = st.text_input("பக்கங்களின் புதிய வரிசை (நீக்க வேண்டியவற்றைத் தவிர்க்கவும்):", f"1-{total}" if total > 1 else "1", key="t3_o")
        angle = st.selectbox("Rotate Angle", [0, 90, 180, 270], key="t3_a")
        rot_s = st.text_input("Rotate Specific Pages (காலியாக விட்டால் அனைத்தும்):", "", key="t3_r")
        if st.button("Apply Page Changes", key="b3"):
            ordered = eng.parse_page_ranges(order_s, total, preserve_order=True)
            targets = set(eng.parse_page_ranges(rot_s, total)) if rot_s.strip() else set(range(total))
            if not ordered:
                st.error("⚠️ சரியான வரிசையை உள்ளிடவும்.")
            else:
                st.download_button("⬇️ Download Updated PDF", eng.transform_pages(raw, ordered, angle, targets), f"Updated_{f.name}", "application/pdf")

elif tool == "4. 📐 Crop Pages (வெட்ட)":
    st.subheader("📐 PDF பக்கங்களின் ஓரங்களை வெட்டி எடுக்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t4")
    if f:
        raw = f.read()
        c1, c2, c3, c4 = st.columns(4)
        l = c1.slider("Left %", 0, 45, 5, key="t4_l")
        r = c2.slider("Right %", 0, 45, 5, key="t4_r")
        t = c3.slider("Top %", 0, 45, 5, key="t4_t")
        b = c4.slider("Bottom %", 0, 45, 5, key="t4_b")
        st.image(eng.crop_pdf(raw, l, r, t, b, preview_only=True), width=380, caption="Page 1 Preview")
        if st.button("Crop All Pages", key="b4"):
            st.download_button("⬇️ Download Cropped PDF", eng.crop_pdf(raw, l, r, t, b), f"Cropped_{f.name}", "application/pdf")

elif tool == "5. 🖋️ Add Stamp / Sign (சீல்)":
    st.subheader("🖋️ PDF-ல் சீல் அல்லது கையொப்பம் பதிக்க")
    c1, c2 = st.columns(2)
    pf = c1.file_uploader("PDF ஃபைல்", type=["pdf"], key="t5_p")
    sf = c2.file_uploader("Stamp / Sign Image", type=["png", "jpg", "jpeg"], key="t5_s")
    if pf and sf:
        praw, sraw = pf.read(), sf.read()
        with fitz.open(stream=praw, filetype="pdf") as d:
            total = len(d)
        k1, k2, k3, k4 = st.columns(4)
        pno = k1.number_input("Page", 1, total, total, key="t5_pn")
        xp = k2.slider("X %", 0, 90, 65, key="t5_x")
        yp = k3.slider("Y %", 0, 90, 75, key="t5_y")
        wp = k4.slider("Width px", 40, 300, 120, key="t5_w")
        st.image(eng.add_stamp_to_page(praw, sraw, pno, xp, yp, wp, preview_only=True), width=400, caption="Preview")
        if st.button("Apply Stamp", key="b5"):
            st.download_button("⬇️ Download Signed PDF", eng.add_stamp_to_page(praw, sraw, pno, xp, yp, wp), f"Signed_{pf.name}", "application/pdf")

elif tool == "6. 💧 Watermark & Page Numbers":
    st.subheader("💧 Watermark மற்றும் Custom Page Numbers சேர்க்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t6")
    if f:
        raw = f.read()
        c1, c2 = st.columns(2)
        add_wm = c1.checkbox("Add Watermark", True, key="t6_aw")
        wm_txt = c1.text_input("Watermark Text", "COPY ONLY", key="t6_wt")
        wm_op = c1.slider("Opacity", 0.05, 0.60, 0.20, 0.05, key="t6_wo")
        wm_fs = c1.slider("Font Size", 24, 96, 52, 4, key="t6_wf")
        add_p = c2.checkbox("Add Page Numbers", True, key="t6_ap")
        p_pre = c2.text_input("Prefix", "Page", key="t6_pp")
        p_pos = c2.selectbox("Position", ["Bottom Center", "Bottom Right", "Bottom Left", "Top Right", "Top Center", "Top Left"], key="t6_po")
        col_sel = c2.selectbox("Color", ["Gray", "Red", "Blue"], key="t6_co")
        cmap = {"Gray": (0.5, 0.5, 0.5), "Red": (0.85, 0.15, 0.15), "Blue": (0.12, 0.25, 0.68)}
        if st.button("Apply Watermark & Page Numbers", key="b6"):
            out = eng.apply_watermark_and_pageno(raw, add_wm, wm_txt, wm_op, wm_fs, cmap[col_sel], add_p, p_pre, p_pos)
            st.download_button("⬇️ Download Updated PDF", out, f"Stamped_{f.name}", "application/pdf")

elif tool == "7. 🔐 Lock PDF (பாஸ்வேர்ட் போட)":
    st.subheader("🔐 PDF-க்கு பாஸ்வேர்ட் போட (AES-256)")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t7")
    if f:
        raw = f.read()
        upw = st.text_input("Open Password", type="password", key="t7_u")
        opw = st.text_input("Owner Password (optional)", type="password", key="t7_o")
        ap = st.checkbox("Allow Printing", True, key="t7_p")
        if st.button("Lock PDF", key="b7"):
            ok, msg, data = eng.lock_or_unlock_pdf(raw, True, upw, opw, ap)
            (st.success if ok else st.error)(msg)
            if data:
                st.download_button("⬇️ Download Locked PDF", data, f"Locked_{f.name}", "application/pdf")

elif tool == "8. 🔓 Unlock PDF (பாஸ்வேர்ட் நீக்க)":
    st.subheader("🔓 PDF பாஸ்வேர்ட் நீக்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t8")
    if f:
        raw = f.read()
        cpw = st.text_input("Current Password", type="password", key="t8_c")
        if st.button("Unlock PDF", key="b8"):
            ok, msg, data = eng.lock_or_unlock_pdf(raw, False, cpw)
            (st.success if ok else st.error)(msg)
            if data:
                st.download_button("⬇️ Download Unlocked PDF", data, f"Unlocked_{f.name}", "application/pdf")

elif tool == "9. 🛡️ Smart Redact (தகவல் மறைப்பு)":
    st.subheader("🛡️ தனிப்பட்ட தகவல்களை நிரந்தரமாக மறைக்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t9")
    if f:
        raw = f.read()
        c1, c2 = st.columns(2)
        terms_s = c1.text_area("Custom Terms (line or comma separated)", height=110, key="t9_t")
        ap = c2.checkbox("Auto-detect 10-digit Phone", True, key="t9_p")
        aa = c2.checkbox("Auto-detect 12-digit Aadhaar", True, key="t9_a")
        ae = c2.checkbox("Auto-detect Email", False, key="t9_e")
        col = c2.radio("Color", ["Black", "White"], horizontal=True, key="t9_c")
        if st.button("Apply Smart Redact", key="b9"):
            terms = [x.strip() for x in terms_s.replace(",", "\n").splitlines() if x.strip()]
            out, cnt = eng.smart_redact(raw, terms, ap, aa, ae, (0, 0, 0) if col == "Black" else (1, 1, 1))
            if not out:
                st.warning("⚠️ பொருந்தும் உரை/எண்கள் எதுவும் கிடைக்கவில்லை.")
            else:
                st.success(f"✅ {cnt} இடங்களில் Redact செய்யப்பட்டது.")
                st.download_button("⬇️ Download Redacted PDF", out, f"Redacted_{f.name}", "application/pdf")

elif tool == "10. 🧹 Metadata Cleaner":
    st.subheader("🧹 PDF Metadata நீக்க")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t10")
    if f:
        raw = f.read()
        meta, _ = eng.inspect_and_clean_metadata(raw, clean=False)
        st.json(meta)
        if st.button("Clean All Metadata", key="b10"):
            _, cleaned = eng.inspect_and_clean_metadata(raw, clean=True)
            st.success("✅ Metadata நீக்கப்பட்டது.")
            st.download_button("⬇️ Download Clean PDF", cleaned, f"Clean_{f.name}", "application/pdf")

elif tool == "11. 🗜️ Smart Compress (Target KB)":
    st.subheader("🗜️ Smart Compress (with Target KB)")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t11")
    if f:
        raw = f.read()
        st.write(f"Original Size: *{len(raw)/1024:.1f} KB*")
        use_target = st.checkbox("Target KB குறிக்கவும் (Auto-adjust)", value=False, key="t11_u")
        target_kb = st.number_input("Target Size (KB)", min_value=20.0, value=250.0, step=10.0, key="t11_k") if use_target else None
        dpi = st.slider("DPI", 50, 200, 110, 10, disabled=use_target, key="t11_d")
        qual = st.slider("JPEG Quality %", 20, 95, 65, 5, disabled=use_target, key="t11_q")
        if st.button("Compress PDF", key="b11"):
            out = eng.compress_pdf_smart(raw, dpi=dpi, quality=qual, target_kb=target_kb)
            st.success(f"✅ New Size: *{len(out)/1024:.1f} KB*")
            st.download_button("⬇️ Download Compressed PDF", out, f"Compressed_{f.name}", "application/pdf")

elif tool == "12. 📦 Batch Compress (பல ஃபைல்கள்)":
    st.subheader("📦 Batch Compress (Multiple PDFs -> ZIP)")
    files = st.file_uploader("PDF ஃபைல்கள்", type=["pdf"], accept_multiple_files=True, key="t12")
    if files:
        dpi = st.slider("DPI", 60, 200, 110, 10, key="t12_d")
        qual = st.slider("Quality %", 25, 90, 65, 5, key="t12_q")
        if st.button("Compress All", key="b12"):
            zip_items = [(f"Compressed_{f.name}", eng.compress_pdf_smart(f.read(), dpi=dpi, quality=qual)) for f in files]
            st.download_button("📦 Download ZIP", eng.build_zip(zip_items), "Batch_Compressed.zip", "application/zip")

elif tool == "13. 💦 Batch Watermark (பல ஃபைல்கள்)":
    st.subheader("💦 Batch Watermark (Multiple PDFs -> ZIP)")
    files = st.file_uploader("PDF ஃபைல்கள்", type=["pdf"], accept_multiple_files=True, key="t13")
    if files:
        wm = st.text_input("Watermark Text", "VERIFIED COPY", key="t13_w")
        op = st.slider("Opacity", 0.05, 0.50, 0.20, 0.05, key="t13_o")
        if st.button("Watermark All", key="b13"):
            zip_items = [(f"Watermarked_{f.name}", eng.apply_watermark_and_pageno(f.read(), True, wm, op, add_pageno=False)) for f in files]
            st.download_button("📦 Download ZIP", eng.build_zip(zip_items), "Batch_Watermarked.zip", "application/zip")

elif tool == "14. 🪪 A4 Sheet Imposition (2-Up / 4-Up)":
    st.subheader("🪪 A4 Sheet Imposition (ID / Certificate Layout)")
    files = st.file_uploader("PDF ஃபைல்கள்", type=["pdf"], accept_multiple_files=True, key="t14")
    if files:
        mode = st.selectbox("Layout", ["2-Up", "4-Up"], key="t14_m")
        border = st.checkbox("Cut Border", True, key="t14_c")
        if st.button("Generate A4 Sheet", key="b14"):
            out, sheets = eng.impose_a4_sheet([(f.name, f.read()) for f in files], mode=mode, add_border=border)
            st.success(f"✅ {sheets} A4 Sheets உருவாக்கப்பட்டன.")
            st.download_button("⬇️ Download A4 PDF", out, "A4_Imposed.pdf", "application/pdf")

elif tool == "15. 🖼️ Extract Embedded Images":
    st.subheader("🖼️ Extract Embedded Images from PDF")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t15")
    if f and st.button("Extract Images", key="b15"):
        imgs = eng.extract_embedded_images(f.read())
        if not imgs:
            st.warning("⚠️ படங்கள் எதுவும் கிடைக்கவில்லை.")
        else:
            st.success(f"✅ {len(imgs)} படங்கள் கிடைத்தன.")
            st.download_button("📦 Download ZIP", eng.build_zip(imgs), "Embedded_Images.zip", "application/zip")

elif tool == "16. 🖼️ Images to PDF (படங்களை மாற்ற)":
    st.subheader("🖼️ JPG / PNG படங்களை ஒரே PDF-ஆக மாற்ற")
    imgs = st.file_uploader("Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="t16")
    out_n = st.text_input("PDF Name", "Images_Output.pdf", key="t16_n")
    if imgs and st.button("Convert to PDF", key="b16"):
        out = eng.images_to_pdf([(i.name, i.read()) for i in imgs])
        st.download_button("⬇️ Download PDF", out, out_n if out_n.endswith(".pdf") else f"{out_n}.pdf", "application/pdf")

elif tool == "17. 📸 PDF to Images (JPG / PNG)":
    st.subheader("📸 PDF பக்கங்களை JPG / PNG படங்களாக மாற்ற")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t17")
    if f:
        raw = f.read()
        with fitz.open(stream=raw, filetype="pdf") as d:
            total = len(d)
        fmt = st.selectbox("Format", ["PNG", "JPG"], key="t17_f")
        dpi = st.selectbox("DPI", [150, 200, 300], index=1, key="t17_d")
        rng = st.text_input("Pages (காலியாக விட்டால் அனைத்தும்)", "", key="t17_r")
        if st.button("Convert to Images", key="b17"):
            idxs = eng.parse_page_ranges(rng, total) if rng.strip() else list(range(total))
            res = eng.pdf_to_images(raw, idxs, fmt=fmt, dpi=dpi)
            if len(res) > 1:
                st.download_button("📦 Download All (.ZIP)", eng.build_zip(res), "PDF_Pages.zip", "application/zip")
            for fn, fb in res:
                st.image(fb, caption=fn, width=360)
                st.download_button(f"⬇️ {fn}", fb, fn, f"image/{fmt.lower()}", key=f"img17_{fn}")

elif tool == "18. 🔍 OCR Text Extract (தமிழ் + Eng)":
    st.subheader("🔍 OCR Text Extract (Tamil + English)")
    up = st.file_uploader("PDF or Image", type=["pdf", "jpg", "jpeg", "png"], key="t18")
    lang = st.selectbox("Language", ["tam+eng", "eng", "tam"], key="t18_l")
    force = st.checkbox("Force OCR (Legacy Font)", False, key="t18_f")
    enh = st.checkbox("Contrast Enhance", True, key="t18_e")
    dpi = st.slider("OCR DPI", 200, 400, 350, 50, key="t18_d")
    if up and st.button("Run OCR", key="b18"):
        txt = eng.extract_text_ocr(up.read(), up.name.lower().endswith(".pdf"), lang=lang, force_ocr=force, dpi=dpi, enhance_img=enh)
        st.text_area("Extracted Text", txt, height=300, key="t18_out")
        st.download_button("⬇️ Download .TXT", txt.encode("utf-8"), f"{up.name.rsplit('.', 1)[0]}_OCR.txt", "text/plain")

elif tool == "19. 📝 PDF to Word (.docx)":
    st.subheader("📝 PDF-ஐ Word (.docx) & .txt கோப்பாக மாற்ற")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t19")
    fb_ocr = st.checkbox("OCR Fallback for Scanned Pages", True, key="t19_o")
    if f and st.button("Convert to Word", key="b19"):
        docx_b, txt_s = eng.pdf_to_docx_and_txt(f.read(), ocr_fallback=fb_ocr)
        base = f.name.rsplit(".", 1)[0]
        c1, c2 = st.columns(2)
        c1.download_button("⬇️ Download .DOCX", docx_b, f"{base}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        c2.download_button("⬇️ Download .TXT", txt_s.encode("utf-8"), f"{base}.txt", "text/plain")

elif tool == "20. 📊 PDF Table to Excel (.xlsx)":
    st.subheader("📊 PDF Table to Excel (.xlsx)")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t20")
    if f and st.button("Extract Tables to Excel", key="b20"):
        dfs, xbytes = eng.extract_tables_to_excel(f.read())
        if not dfs:
            st.warning("⚠️ Tables எதுவும் கிடைக்கவில்லை.")
        else:
            for sname, df in dfs:
                st.write(f"*{sname}*")
                st.dataframe(df, use_container_width=True)
            st.download_button("⬇️ Download Excel (.xlsx)", xbytes, f"{f.name.rsplit('.', 1)[0]}_Tables.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif tool == "21. 🖍️ Search & Highlight / Replace":
    st.subheader("🖍️ Search & Highlight அல்லது Find & Replace")
    f = st.file_uploader("PDF ஃபைல்", type=["pdf"], key="t21")
    if f:
        raw = f.read()
        sub_mode = st.radio("செயல்பாடு:", ["Highlight Keywords", "Find & Replace (Overlay)"], horizontal=True, key="t21_m")
        if sub_mode == "Highlight Keywords":
            kw = st.text_input("Keywords (comma separated)", "", key="t21_k")

            terms = [x.strip() for x in kw.split(",") if x.strip()]
            if st.button("Highlight Keywords", key="b21h"):
                if not terms:
                    st.warning("Enter at least one keyword.")
                else:
                    out, hits = eng.highlight_terms(raw, terms)
                    if out:
                        st.success(f"{hits} matches highlighted.")
                        st.download_button("Download Highlighted PDF", out, f"Highlighted_{f.name}", "application/pdf")
                    else:
                        st.warning("No matching text found.")
        else:
            c1, c2 = st.columns(2)
            find_s = c1.text_input("Find text", key="t21_find")
            replace_s = c2.text_input("Replace with", key="t21_replace")
            if st.button("Find & Replace", key="b21r"):
                if not find_s:
                    st.warning("Enter text to find.")
                else:
                    out, count = eng.find_and_replace_overlay(raw, find_s, replace_s)
                    if out:
                        st.success(f"{count} occurrence(s) replaced.")
                        st.download_button("Download Updated PDF", out, f"Replaced_{f.name}", "application/pdf")
                    else:
                        st.warning("No matching text found.")

elif tool == "22. Image Studio (Resize / Compress / Convert / Print)":
    import image_engine as imgeng
    st.subheader("Image Studio — Resize, Compress, Convert & Print")
    st.caption("Images are processed in memory during this session. Choose a tool below.")
    mode = st.selectbox("Choose image tool", [
        "Resize Image", "Compress to KB", "Convert Format", "Crop / Rotate / Flip",
        "DPI & Print Size", "Add Text / Watermark", "Batch Resize & Compress",
        "Passport / Visa Photo Sheet", "Image Adjustments", "View Image Information"
    ], key="img_mode")
    if mode == "Resize Image":
        f = st.file_uploader("Upload image", type=["png","jpg","jpeg","webp","bmp"], key="im_resize")
        if f:
            raw = f.getvalue()
            preview = imgeng.image_info(raw)
            st.image(raw, caption=f"Original: {preview['width']} × {preview['height']} px", use_container_width=True)
            unit = st.selectbox("Resize method", ["Pixels", "Percentage", "Centimeters", "Inches"], key="im_unit")
            if unit == "Pixels":
                c1,c2 = st.columns(2)
                w = c1.number_input("Width (px)", 1, 12000, preview["width"], key="im_w")
                h = c2.number_input("Height (px)", 1, 12000, preview["height"], key="im_h")
            elif unit == "Percentage":
                pct = st.slider("Scale (%)", 1, 400, 50, key="im_pct")
                w = max(1, int(preview["width"]*pct/100)); h = max(1, int(preview["height"]*pct/100))
            else:
                dpi = st.number_input("Output DPI", 72, 1200, 300, key="im_dpi")
                c1,c2 = st.columns(2)
                wv = c1.number_input(f"Width ({'cm' if unit=='Centimeters' else 'inches'})", 0.1, 100.0, round(preview["width"]/300*(2.54 if unit=="Centimeters" else 1),2), key="im_wv")
                hv = c2.number_input(f"Height ({'cm' if unit=='Centimeters' else 'inches'})", 0.1, 100.0, round(preview["height"]/300*(2.54 if unit=="Centimeters" else 1),2), key="im_hv")
                factor = dpi/(2.54 if unit=="Centimeters" else 1)
                w,h = int(wv*factor),int(hv*factor)
            keep = st.checkbox("Keep aspect ratio", True, key="im_keep")
            if keep:
                ratio = preview["width"]/preview["height"]
                if w/h > ratio: w = int(h*ratio)
                else: h = int(w/ratio)
            fmt = st.selectbox("Output format", ["PNG","JPEG","WEBP"], key="im_resize_fmt")
            quality = st.slider("Quality", 10, 100, 92, key="im_resize_q") if fmt != "PNG" else 100
            if st.button("Resize Image", key="im_resize_go"):
                out = imgeng.resize_image(raw,w,h,fmt,quality)
                st.image(out, caption=f"Output: {w} × {h} px", use_container_width=True)
                st.download_button("Download resized image",out,f"resized.{fmt.lower()}",f"image/{fmt.lower()}")
    elif mode == "Compress to KB":
        f = st.file_uploader("Upload image", type=["png","jpg","jpeg","webp"], key="im_kb")
        if f:
            raw=f.getvalue()
            st.write(f"Original size: {len(raw)/1024:.1f} KB")
            target=st.number_input("Target file size (KB)",1,20000,100,key="im_target")
            fmt=st.selectbox("Format",["JPEG","WEBP"],key="im_kbfmt")
            if st.button("Compress image",key="im_kbgo"):
                out, reached=imgeng.compress_to_target(raw,target,fmt)
                st.write(f"Output: {len(out)/1024:.1f} KB")
                if not reached: st.warning("Target could not be reached at the safe minimum quality; this is the smallest result found.")
                st.image(out, use_container_width=True)
                st.download_button("Download compressed image",out,f"compressed.{fmt.lower()}",f"image/{fmt.lower()}")
    elif mode == "Convert Format":
        f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp","bmp","tiff"],key="im_conv")
        if f:
            fmt=st.selectbox("Convert to",["PNG","JPEG","WEBP","BMP","TIFF"],key="im_convfmt")
            q=st.slider("Quality (JPEG / WEBP)",10,100,92,key="im_convq")
            if st.button("Convert",key="im_convgo"):
                out=imgeng.convert_image(f.getvalue(),fmt,q)
                st.image(out,use_container_width=True)
                st.download_button("Download converted image",out,f"converted.{fmt.lower()}",f"image/{fmt.lower()}")
    elif mode == "Crop / Rotate / Flip":
        f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp"],key="im_crop")
        if f:
            raw=f.getvalue(); info=imgeng.image_info(raw)
            st.image(raw,use_container_width=True)
            c1,c2,c3,c4=st.columns(4)
            left=c1.slider("Left crop %",0,45,0,key="im_l")
            right=c2.slider("Right crop %",0,45,0,key="im_r")
            top=c3.slider("Top crop %",0,45,0,key="im_t")
            bottom=c4.slider("Bottom crop %",0,45,0,key="im_b")
            angle=st.selectbox("Rotate", [0,90,180,270],key="im_angle")
            flip=st.selectbox("Flip",["None","Horizontal","Vertical"],key="im_flip")
            if st.button("Apply crop / rotate / flip",key="im_cropgo"):
                out=imgeng.transform_image(raw,left,right,top,bottom,angle,flip)
                st.image(out,use_container_width=True)
                st.download_button("Download edited image",out,"edited.png","image/png")
    elif mode == "DPI & Print Size":
        f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp"],key="im_dpi")
        if f:
            raw=f.getvalue(); info=imgeng.image_info(raw)
            st.write(f"Current dimensions: {info['width']} × {info['height']} px")
            dpi=st.selectbox("Print DPI",[72,150,200,300,600],index=3,key="im_printdpi")
            width=st.number_input("Print width (inches)",0.1,100.0,4.0,key="im_printw")
            height=st.number_input("Print height (inches)",0.1,100.0,6.0,key="im_printh")
            if st.button("Prepare print image",key="im_printgo"):
                out=imgeng.resize_image(raw,int(width*dpi),int(height*dpi),"JPEG",95)
                st.success(f"Prepared at {int(width*dpi)} × {int(height*dpi)} px, {dpi} DPI")
                st.download_button("Download print-ready image",out,"print_ready.jpg","image/jpeg")
    elif mode == "Add Text / Watermark":
        f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp"],key="im_wm")
        if f:
            text_value=st.text_input("Text / watermark", "SAMPLE")
            pos=st.selectbox("Position",["Center","Top Left","Top Right","Bottom Left","Bottom Right"])
            opacity=st.slider("Opacity",10,100,45)
            size=st.slider("Font size",12,180,48)
            if st.button("Add watermark",key="im_wmgo"):
                out=imgeng.add_watermark(f.getvalue(),text_value,pos,opacity,size)
                st.image(out,use_container_width=True)
                st.download_button("Download watermarked image",out,"watermarked.png","image/png")
    elif mode == "Batch Resize & Compress":
        files=st.file_uploader("Select multiple images",type=["png","jpg","jpeg","webp"],accept_multiple_files=True,key="im_batch")
        if files:
            width=st.number_input("Maximum width (px)",1,12000,1200,key="im_bw")
            quality=st.slider("Quality",10,100,85,key="im_bq")
            fmt=st.selectbox("Output format",["JPEG","WEBP","PNG"],key="im_bfmt")
            if st.button("Process all images",key="im_batchgo"):
                outputs=[]
                for file in files:
                    outputs.append((f"{pathlib.Path(file.name).stem}_processed.{fmt.lower()}",imgeng.fit_within(file.getvalue(),width,fmt,quality)))
                archive=eng.build_zip(outputs)
                st.success(f"Processed {len(outputs)} image(s).")
                st.download_button("Download all as ZIP",archive,"processed_images.zip","application/zip")
    elif mode == "Passport / Visa Photo Sheet":
        f=st.file_uploader("Upload portrait photo",type=["png","jpg","jpeg"],key="im_pass")
        if f:
            st.image(f.getvalue(),width=220)
            preset=st.selectbox("Photo size",["Indian passport photo — 35 × 45 mm","Visa photo — 2 × 2 inches","Custom"])
            dpi=st.selectbox("DPI",[300,600],index=0)
            if preset.startswith("Indian"):
                pw,ph=35,45
            elif preset.startswith("Visa"):
                pw,ph=50.8,50.8
            else:
                c1,c2=st.columns(2); pw=c1.number_input("Width (mm)",5.0,100.0,35.0); ph=c2.number_input("Height (mm)",5.0,100.0,45.0)
            copies=st.slider("Number of copies",1,40,8)
            if st.button("Create A4 photo sheet",key="im_passgo"):
                out=imgeng.photo_sheet(f.getvalue(),pw,ph,copies,dpi)
                st.download_button("Download A4 photo sheet PDF",out,"photo_sheet.pdf","application/pdf")
    elif mode == "Image Adjustments":
        f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp"],key="im_adj")
        if f:
            c1,c2,c3=st.columns(3)
            bright=c1.slider("Brightness",0.2,2.0,1.0,0.05)
            contrast=c2.slider("Contrast",0.2,2.0,1.0,0.05)
            sharp=c3.slider("Sharpness",0.0,3.0,1.0,0.05)
            if st.button("Apply adjustments",key="im_adjgo"):
                out=imgeng.adjust_image(f.getvalue(),bright,contrast,sharp)
                st.image(out,use_container_width=True)
                st.download_button("Download adjusted image",out,"adjusted.png","image/png")
    else:
        f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp","bmp","tiff"],key="im_info")
        if f:
            st.json(imgeng.image_info(f.getvalue()))
